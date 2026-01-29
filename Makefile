.PHONY: help build up down restart logs logs-app logs-db check-db test-db clean clean-invalid

help:
	@echo "AutoRia Scraper - Available commands:"
	@echo ""
	@echo "  make build        - Build Docker containers"
	@echo "  make up           - Start the application"
	@echo "  make down         - Stop the application"
	@echo "  make restart      - Restart the application"
	@echo "  make logs         - View all logs"
	@echo "  make logs-app     - View application logs"
	@echo "  make logs-db      - View database logs"
	@echo "  make check-db     - Check database contents"
	@echo "  make test-db      - Test database connection"
	@echo "  make clean-invalid - Remove invalid records (429 errors, etc)"
	@echo "  make clean        - Remove all containers and volumes"
	@echo ""

build:
	docker-compose build

up:
	docker-compose up -d
	@echo "Application started! Use 'make logs-app' to view logs"

down:
	docker-compose down

restart:
	docker-compose restart app

logs:
	docker-compose logs -f

logs-app:
	docker-compose logs -f app

logs-db:
	docker-compose logs -f db

check-db:
	docker-compose exec app python check_db.py

test-db:
	docker-compose exec app python test_db_connection.py

clean-invalid:
	docker-compose exec app python clean_db.py

clean:
	docker-compose down -v
	@echo "All containers and volumes removed!"
