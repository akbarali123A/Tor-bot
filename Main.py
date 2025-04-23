import asyncio
from playwright.async_api import async_playwright
from stem import Signal
from stem.control import Controller
import random
import geoip2.database
from fake_useragent import UserAgent
import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class AutoBot:
    def __init__(self):
        self.ua = UserAgent()
        self.geoip = geoip2.database.Reader('/app/GeoLite2-City.mmdb')
        self.tor_proxy = "socks5://127.0.0.1:9050"
        self.ip_tracker = {}
        self.max_clicks = 2
        
    async def rotate_identity(self):
        with Controller.from_port(port=9051) as ctrl:
            ctrl.authenticate()
            ctrl.signal(Signal.NEWNYM)
        logging.info("New Tor circuit created")

    async def get_fingerprint(self):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(proxy={'server': self.tor_proxy})
            page = await context.new_page()
            await page.goto('http://icanhazip.com')
            ip = (await page.text_content('body')).strip()
            await browser.close()

        return {
            'user_agent': self.ua.random,
            'ip': ip,
            'timezone': self.geoip.city(ip).location.time_zone or 'Asia/Kolkata',
            'resolution': f"{random.randint(1280,1920)}x{random.randint(720,1080)}"
        }

    async def human_interaction(self, page):
        # Random mouse movements
        for _ in range(random.randint(3,7)):
            x = random.randint(0, 1920)
            y = random.randint(0, 1080)
            await page.mouse.move(x, y)
            await page.wait_for_timeout(random.randint(200, 800))
        
        # Random scrolling
        await page.evaluate(f"window.scrollBy(0, {random.randint(300, 1000)})")
        await page.wait_for_timeout(random.randint(1000, 3000))

    async def process_url(self, url):
        try:
            await self.rotate_identity()
            fp = await self.get_fingerprint()
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=[f"--window-size={fp['resolution']}"]
                )
                
                context = await browser.new_context(
                    user_agent=fp['user_agent'],
                    timezone_id=fp['timezone'],
                    proxy={'server': self.tor_proxy}
                )
                
                page = await context.new_page()
                await page.goto(url, timeout=60000)
                await self.human_interaction(page)
                
                # Ad click logic
                ads = await page.query_selector_all('a[href*="ads"],iframe[src*="ad"]')
                if ads and self.ip_tracker.get(fp['ip'], 0) < self.max_clicks:
                    await random.choice(ads).click()
                    self.ip_tracker[fp['ip']] = self.ip_tracker.get(fp['ip'], 0) + 1
                    logging.info(f"Clicked ad using {fp['ip']}")

                await page.wait_for_timeout(random.randint(5000, 15000))
                await context.close()
                
        except Exception as e:
            logging.error(f"Error processing {url}: {str(e)}")

    async def run(self, urls):
        while True:
            tasks = [self.process_url(url) for url in urls]
            await asyncio.gather(*tasks)
            await asyncio.sleep(random.randint(1800, 3600))  # 30-60 mins

if __name__ == "__main__":
    bot = AutoBot()
    asyncio.run(bot.run(["https://dophejibi.com/c7YbA2","https://646499.shop/a937a5cf6406c7d848b2/9ece5d23a0/?placementName=default","https://reyeshehadtwobri.com?K5tYl=1172346"]))  # Add your URLs here
