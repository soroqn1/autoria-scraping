import asyncio
import os
import subprocess
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.database import init_db
from app.scraper import scraper

async def run_dump():
    print("Starting DB dump...")
    os.makedirs("/app/dumps", exist_ok=True)
    filename = f"/app/dumps/dump_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
    try:
        env = os.environ.copy()
        env["PGPASSWORD"] = os.getenv("POSTGRES_PASSWORD", "postgres")
        
        cmd = [
            "pg_dump",
            "-h", "db",
            "-U", os.getenv("POSTGRES_USER", "postgres"),
            "-d", os.getenv("POSTGRES_DB", "autoria_db"),
            "-f", filename
        ]
        subprocess.run(cmd, env=env, check=True)
        print(f"Dump saved to {filename}")
    except Exception as e:
        print(f"Error during dump: {e}")

async def scheduled_scraping():
    await scraper.run()

async def main():
    print("Application starting...")
    await init_db()
    
    scheduler = AsyncIOScheduler()
    
    scrape_time = os.getenv("SCRAPE_TIME", "12:00").split(":")
    dump_time = os.getenv("DUMP_TIME", "12:00").split(":")
    
    scheduler.add_job(scheduled_scraping, 'cron', hour=scrape_time[0], minute=scrape_time[1])
    scheduler.add_job(run_dump, 'cron', hour=dump_time[0], minute=dump_time[1])
    
    print(f"Scheduler started. Scrape at {scrape_time[0]}:{scrape_time[1]}, Dump at {dump_time[0]}:{dump_time[1]}")
    
    scheduler.start()
    
    await scheduled_scraping() 
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Initial scrape completed.")
    print(f"Next scrape: {scrape_time[0]}:{scrape_time[1]} daily.")

    try:
        while True:
            await asyncio.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        pass

if __name__ == "__main__":
    asyncio.run(main())
