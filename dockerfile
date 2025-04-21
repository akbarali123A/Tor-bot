FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    tor \
    wget \
    unzip \
    xvfb \
    curl

ARG MAXMIND_LICENSE_KEY
RUN echo "Downloading GeoIP database with license key: ${MAXMIND_LICENSE_KEY}" && \
    wget "https://download.maxmind.com/geoip/databases/GeoIP2-City/download?suffix=tar.gz&license_key=${MAXMIND_LICENSE_KEY}" -O GeoLite2-City.tar.gz || (echo "Download failed"; exit 1) && \
    tar -xzf GeoLite2-City.tar.gz && \
    mv GeoLite2-City_*/GeoLite2-City.mmdb . && \
    echo "GeoLite2-City.mmdb file exists:" && \
    ls -lah GeoLite2-City.mmdb && \
    rm -rf GeoLite2-City_*

COPY requirements.txt .
RUN pip install -r requirements.txt

RUN playwright install chromium

COPY . .

CMD ["sh", "-c", "tor & Xvfb :99 -screen 0 1920x1080x16 & export DISPLAY=:99 && python main.py"]
