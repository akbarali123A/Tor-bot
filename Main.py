import asyncio
from playwright.async_api import async_playwright
from stem import Signal
from stem.control import Controller
import random
import geoip2.database
from fake_useragent import UserAgent
import datetime

class UltimateBot:
    def __init__(self):
        self.ua = UserAgent()
        self.geoip = geoip2.database.Reader('GeoLite2-City.mmdb')
        self.tor_proxy = "socks5://127.0.0.1:9050"
        self.ip_tracker = {}
        self.max_clicks_per_ip = 2
        self.viewport_options = {
            'desktop': [(1280, 720), (1366, 768), (1440, 900), (1920, 1080)],
            'mobile': [(360, 640), (414, 896), (375, 812)]
        }

    async def _rotate_tor_identity(self):
        with Controller.from_port(port=9051) as controller:
            controller.authenticate()
            controller.signal(Signal.NEWNYM)
        await asyncio.sleep(10)  # Tor circuit rebuild time

    async def _get_current_ip(self):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(proxy={'server': self.tor_proxy})
            page = await context.new_page()
            await page.goto('http://icanhazip.com')
            ip = (await page.text_content('body')).strip()
            await browser.close()
            return ip

    def _generate_fingerprint(self, ip):
        try:
            timezone = self.geoip.city(ip).location.time_zone
        except:
            timezone = 'Asia/Kolkata'

        device_type = random.choice(['desktop', 'mobile'])
        width, height = random.choice(self.viewport_options[device_type])

        return {
            'user_agent': self.ua.random,
            'viewport': {'width': width, 'height': height},
            'timezone': timezone,
            'platform': 'Win32' if device_type == 'desktop' else 'Linux armv8l',
            'device_type': device_type
        }

    async def _human_like_interaction(self, page):
        # स्क्रॉल बिहेवियर
        scroll_patterns = [
            (random.randint(300, 500), 
            (random.randint(100, 300)),
            (random.randint(50, 200))
        ]
        for scroll_amount in scroll_patterns:
            await page.evaluate(f"window.scrollBy(0, {scroll_amount})")
            await page.wait_for_timeout(random.randint(500, 1500))

        # माउस मूवमेंट
        for _ in range(random.randint(3, 5)):
            x = random.randint(0, 1920)
            y = random.randint(0, 1080)
            await page.mouse.move(x, y, steps=random.randint(5, 15))
            await page.wait_for_timeout(random.randint(200, 800))

    async def _smart_ad_interaction(self, page, ip):
        ad_selectors = [
            ('a[href*="ads"]', 'href'),
            ('iframe[src*="ad"]', 'src'),
            ('div[data-ad-target]', 'data-ad-target'),
            ('img[src*="banner"]', 'src')
        ]

        today = datetime.date.today()
        if ip in self.ip_tracker:
            if self.ip_tracker[ip][0] == today and self.ip_tracker[ip][1] >= self.max_clicks_per_ip:
                return False

        for selector, attr in ad_selectors:
            elements = await page.query_selector_all(selector)
            if elements:
                ad = random.choice(elements)
                await self._human_like_interaction(page)
                await ad.scroll_into_view_if_needed()
                
                box = await ad.bounding_box()
                x = box['x'] + random.uniform(10, box['width']-10)
                y = box['y'] + random.uniform(10, box['height']-10)
                
                await page.mouse.move(x, y, steps=random.randint(5, 15))
                await page.mouse.down()
                await page.wait_for_timeout(random.uniform(0.1, 0.3))
                await page.mouse.up()
                
                # क्लिक ट्रैकिंग
                self.ip_tracker[ip] = (today, self.ip_tracker.get(ip, (None, 0))[1] + 1)
                return True
        return False

    async def _tab_session(self, url):
        await self._rotate_tor_identity()
        ip = await self._get_current_ip()
        fingerprint = self._generate_fingerprint(ip)

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                proxy={'server': self.tor_proxy}
            )
            context = await browser.new_context(
                user_agent=fingerprint['user_agent'],
                viewport=fingerprint['viewport'],
                timezone_id=fingerprint['timezone']
            )

            # एंटी-डिटेक्शन फीचर्स
            await context.add_init_script(f"""
                Object.defineProperty(navigator, 'platform', {{
                    get: () => '{fingerprint['platform']}'
                }});
                Object.defineProperty(navigator, 'hardwareConcurrency', {{
                    value: {random.choice([2, 4, 8])}
                }});
            """)

            page = await context.new_page()
            try:
                # वेबसाइट विजिट
                await page.goto(url, timeout=60000)
                
                # ह्यूमन इंटरेक्शन
                await self._human_like_interaction(page)
                
                # एड इंटरेक्शन
                await self._smart_ad_interaction(page, ip)
                
                # रैंडम एक्टिविटी टाइम
                await page.wait_for_timeout(random.randint(5000, 15000))

            finally:
                await context.close()
                await browser.close()

    async def run_campaign(self, urls):
        while True:
            tasks = [self._tab_session(url) for url in urls]
            await asyncio.gather(*tasks)
            
            # रैंडम वेटिंग इंटरवल
            await asyncio.sleep(random.randint(1800, 3600))  # 30-60 मिनट

if __name__ == "__main__":
    # कॉन्फिगरेशन
    TARGET_URLS = [
        "https://reyeshehadtwobri.com?K5tYl=1172346",
        "https://dophejibi.com/c7YbA2",
      "https://646499.shop/a937a5cf6406c7d848b2/9ece5d23a0/?placementName=default"
    ]
    
    bot = UltimateBot()
    asyncio.run(bot.run_campaign(TARGET_URLS))
