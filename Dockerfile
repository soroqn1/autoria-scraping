FROM python:3.11-slim

# Install postgresql-client and Playwright dependencies
ENV PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y \
    postgresql-client \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install --with-deps chromium

COPY . .

# Ensure dumps directory exists
RUN mkdir -p dumps

CMD ["python", "-m", "app.main"]
