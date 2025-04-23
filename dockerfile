FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tor \
    xvfb \
    wget \
    unzip \
    gcc \
    libffi-dev

# Download GeoIP database
ARG MAXMIND_LICENSE_KEY
RUN wget "https://download.maxmind.com/geoip/databases/GeoIP2-City/download?suffix=tar.gz&license_key=${MAXMIND_LICENSE_KEY}" -O GeoLite2-City.tar.gz \
    && tar -xzf GeoLite2-City.tar.gz \
    && mv GeoLite2-City_*/GeoLite2-City.mmdb /app/ \
    && rm -rf GeoLite2-City*

# Python setup
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install browsers
RUN playwright install chromium

# Copy code
COPY . /app
WORKDIR /app

# Startup command
CMD ["sh", "-c", "tor --RunAsDaemon 1 --ControlPort 9051 --SocksPort 9050 & Xvfb :99 -screen 0 1920x1080x16 & export DISPLAY=:99 && python main.py"]
