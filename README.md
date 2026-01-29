# AutoRia Scraper

Daily scraper for used cars from AutoRia platform using Playwright.

## Data Fields

All fields stored in `cars` table:

| Field | Type | Description |
|-------|------|-------------|
| url | String (PK) | Listing URL |
| title | String | Car title |
| price_usd | Float | Price in USD |
| odometer | BigInteger | Mileage |
| username | String | Seller name |
| phone_number | BigInteger | Phone number |
| image_url | String | Main image URL |
| images_count | BigInteger | Total images |
| car_number | String | License plate |
| car_vin | String | VIN code |
| datetime_found | DateTime | Record timestamp |

## Tech Stack

- **Python 3.11** - async/await
- **Playwright** - browser automation for JS-rendered content
- **SQLAlchemy async** - ORM with asyncpg driver
- **APScheduler** - daily scheduling
- **PostgreSQL 15** - database
- **Docker Compose** - containerization

## Setup

### 1. Clone repository
```bash
git clone https://github.com/soroqn1/autoria-scraping.git
cd autoria-scraping
```

### 2. Create .env file
```bash
cp .env.example .env
```

### 3. Run
```bash
docker-compose up --build
```

Application will:
1. Create database and tables
2. Run initial scrape immediately  
3. Schedule daily runs at configured time

### 4. Check data
```bash
docker-compose exec app python check_db.py
```

Or connect to PostgreSQL:
```bash
docker-compose exec db psql -U postgres -d autoria_db
```

## Features

- Playwright browser automation for JavaScript-rendered content
- Sequential processing with delays (3-6s per car, 10-15s per page)
- Automatic 429 rate limit handling with retry logic
- Duplicate prevention via URL primary key
- Daily SQL dumps in `dumps/` folder
- Comprehensive error handling and logging

## Stop
```bash
docker-compose down        # Stop containers
docker-compose down -v     # Remove all data
```

## License
MIT