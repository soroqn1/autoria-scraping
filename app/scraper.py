import asyncio
import re
import datetime
import random
from playwright.async_api import async_playwright, Page
from .database import async_session, save_car

BASE_URL = "https://auto.ria.com/uk/car/used/"


class AutoRiaScraper:
    def __init__(self):
        self.browser = None
        self.context = None
        
    async def init_browser(self):
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=True)
        self.context = await self.browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            locale="uk-UA"
        )
        
    async def close_browser(self):
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
    
    async def fetch_page_urls(self, page_num):
        url = f"{BASE_URL}?page={page_num}"
        try:
            page = await self.context.new_page()
            await page.goto(url, wait_until="networkidle", timeout=30000)
            
            links = await page.eval_on_selector_all(
                'a[href*="/auto_"]',
                '(elements) => elements.map(el => el.href)'
            )
            
            await page.close()
            
            filtered = [
                link for link in set(links) 
                if "/auto_" in link and "/newauto/" not in link
            ]
            
            return filtered
        except Exception as e:
            print(f"Error fetching page {page_num}: {e}")
            return []
    
    async def scrape_car_details(self, url):
        try:
            await asyncio.sleep(random.uniform(2.0, 4.0))
            
            page = await self.context.new_page()
            response = await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            
            if response.status == 429:
                print(f"  ⚠️  Rate limit, waiting...")
                await page.close()
                await asyncio.sleep(30)
                return None
                
            if response.status != 200:
                await page.close()
                return None
            
            try:
                await page.wait_for_selector('h1', timeout=5000)
            except:
                pass
            
            title = await self.safe_get_text(page, 'h1.head')
            if not title:
                title = await self.safe_get_text(page, 'h1')
            
            if not title or len(title) < 3:
                await page.close()
                return None
            
            price_usd = 0
            price_text = await self.safe_get_text(page, '.price_value strong')
            if not price_text:
                price_text = await self.safe_get_text(page, '.price_value')
            if not price_text:
                price_text = await self.safe_get_text(page, '[data-currency="USD"]')
                
            if price_text:
                price_clean = re.sub(r'[^\d]', '', price_text)
                if price_clean:
                    price_usd = float(price_clean)
            
            odometer = 0
            odo_selectors = [
                '.base-information span',
                'div.base-information__item:has-text("тис. км")',
                'dd:has-text("тис. км")',
                '.technical-info dd:has-text("км")',
            ]
            for selector in odo_selectors:
                odo_text = await self.safe_get_text(page, selector)
                if odo_text and ('км' in odo_text or 'тис' in odo_text):
                    odo_clean = re.sub(r'[^\d]', '', odo_text)
                    if odo_clean:
                        odometer = int(odo_clean)
                        if 'тис' in odo_text:
                            odometer *= 1000
                        break
            
            username = "Unknown"
            seller_selectors = [
                '.seller_info_name',
                '.seller_info_title', 
                'h4.name',
                '.seller-name',
                '[data-qa-id="seller_name"]',
            ]
            for selector in seller_selectors:
                name = await self.safe_get_text(page, selector)
                if name and name != "Unknown":
                    username = name.strip()
                    break
            
            image_url = ""
            img_selectors = [
                'img.outline',
                '.photo-620x465 img',
                '.gallery-order img',
                'picture img',
            ]
            for selector in img_selectors:
                img = await self.safe_get_attr(page, selector, 'src')
                if img:
                    image_url = img
                    break
            
            images_count = 1
            count_text = await self.safe_get_text(page, '.show-all.link-dotted')
            if count_text:
                count_match = re.search(r'\d+', count_text)
                if count_match:
                    images_count = int(count_match.group())
            
            car_number = None
            num_text = await self.safe_get_text(page, '.state-num')
            if num_text:
                car_number = num_text.split()[0] if num_text.strip() else None
            
            car_vin = None
            vin_selectors = ['.label-vin', '.vin-code', 'span.vin-code', '[class*="vin"]']
            for selector in vin_selectors:
                vin = await self.safe_get_text(page, selector)
                if vin and len(vin) == 17:
                    car_vin = vin
                    break
            
            if not car_vin:
                content = await page.content()
                vin_match = re.search(r'\b([A-HJ-NPR-Z0-9]{17})\b', content)
                if vin_match:
                    car_vin = vin_match.group(1)
            
            phone = 0
            try:
                phone_button = await page.query_selector('.phone-show, .show-phone, [data-phone]')
                if phone_button:
                    await phone_button.click()
                    await page.wait_for_timeout(2000)
                    
                    phone_text = await self.safe_get_text(page, '.phone-number, .seller-phone')
                    if phone_text:
                        digits = re.sub(r'\D', '', phone_text)
                        if len(digits) == 10:
                            digits = "38" + digits
                        if digits and len(digits) >= 10:
                            phone = int(digits)
            except:
                pass
            
            await page.close()
            
            return {
                "url": url,
                "title": title,
                "price_usd": price_usd,
                "odometer": odometer,
                "username": username,
                "phone_number": phone,
                "image_url": image_url,
                "images_count": images_count,
                "car_number": car_number,
                "car_vin": car_vin,
                "datetime_found": datetime.datetime.utcnow()
            }
            
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            try:
                await page.close()
            except:
                pass
            return None
    
    async def safe_get_text(self, page: Page, selector: str):
        try:
            element = await page.query_selector(selector)
            if element:
                text = await element.inner_text()
                return text.strip() if text else None
        except:
            pass
        return None
    
    async def safe_get_attr(self, page: Page, selector: str, attr: str):
        try:
            element = await page.query_selector(selector)
            if element:
                return await element.get_attribute(attr)
        except:
            pass
        return None
    
    async def run(self):
        print("="*60)
        print("Starting scraping...")
        print(f"Target: {BASE_URL}")
        print("="*60)
        
        await self.init_browser()
        
        page = 1
        total_saved = 0
        consecutive_empty = 0
        
        try:
            while page <= 1000:
                urls = await self.fetch_page_urls(page)
                
                if not urls:
                    consecutive_empty += 1
                    if consecutive_empty >= 3:
                        print("Three empty pages, stopping.")
                        break
                    page += 1
                    continue
                
                consecutive_empty = 0
                print(f"\nProcessing page {page} ({len(urls)} cars)...")
                
                results = []
                for i, url in enumerate(urls, 1):
                    print(f"  {i}/{len(urls)}: {url.split('/')[-1][:30]}...")
                    car_data = await self.scrape_car_details(url)
                    results.append(car_data)
                    
                    if i < len(urls):
                        await asyncio.sleep(random.uniform(3.0, 6.0))
                
                saved_on_page = 0
                try:
                    async with async_session() as session:
                        async with session.begin():
                            for car_data in filter(None, results):
                                is_new = await save_car(session, car_data)
                                if is_new:
                                    saved_on_page += 1
                    print(f"Page {page} done. Saved {saved_on_page} new cars.")
                except Exception as e:
                    print(f"Error saving page {page}: {e}")
                
                total_saved += saved_on_page
                page += 1
                
                if page <= 1000:
                    await asyncio.sleep(random.uniform(10.0, 15.0))
        
        finally:
            await self.close_browser()
        
        print("="*60)
        print(f"Scraping complete!")
        print(f"Total pages: {page - 1}")
        print(f"Total saved: {total_saved}")
        print("="*60)


scraper = AutoRiaScraper()
