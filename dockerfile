# Base image
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tor \
    xvfb \
    wget \
    unzip \
    gcc \
    libffi-dev \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxi6 \
    libxtst6 \
    libglib2.0-0 \
    libgbm1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libpangocairo-1.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Download GeoIP database
ARG MAXMIND_LICENSE_KEY
RUN wget "https://download.maxmind.com/geoip/databases/GeoIP2-City/download?suffix=tar.gz&license_key=${MAXMIND_LICENSE_KEY}" -O GeoLite2-City.tar.gz \
    && tar -xzf GeoLite2-City.tar.gz \
    && mv GeoLite2-City_*/GeoLite2-City.mmdb /app/ \
    && rm -rf GeoLite2-City*

# Python setup
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright with system dependencies
RUN playwright install --with-deps chromium

# Copy application code
COPY . .

# Startup command with proper initialization sequence
CMD ["sh", "-c", \
    "tor --RunAsDaemon 1 --ControlPort 9051 --SocksPort 9050 & \
    sleep 15 && \
    Xvfb :99 -screen 0 1920x1080x16 & \
    export DISPLAY=:99 && \
    python main.py"]
