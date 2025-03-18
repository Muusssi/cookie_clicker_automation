
import re
import time
from enum import Enum

from playwright.sync_api import sync_playwright

COOKIE_COUNT_REGEX = r"(?P<cookies>[0-9]+) cookies? per second: (?P<per_second>[0-9]+(.[0-9]+)?)"


class Product(Enum):
    Cursor = 0
    Grandma = 1

class CookieClicker():
    def __init__(self, *, headless: bool = False):
        self._playwright = sync_playwright().start()
        self._browser = None
        self.page = None
        self._start(headless)

    def _start(self, headless: bool):
        print("Starting browser")
        self._browser = self._playwright.chromium.launch(headless=headless)
        self.page = self._browser.new_page()
        print("Navigating to cookie clicker")
        self.page.goto("https://orteil.dashnet.org/cookieclicker/")
        print("Consent to cookies and select langauage")
        self.page.get_by_role("button", name="Consent").click()
        self.page.locator("#langSelect-EN").click()
        print("Game ready")

    def click_big_cookie(self):
        self.page.locator("#bigCookie").click()

    def get_cookie_counts(self) -> tuple[int, int]:
        cookies, per_second = 0, 0
        cookie_counts_text = self.page.locator("#cookies").inner_text().replace('\n', ' ')
        result = re.match(COOKIE_COUNT_REGEX, cookie_counts_text)
        if result:
            cookies, per_second = int(result.group('cookies')), float(result.group('per_second'))
        print(f"Cookies: {cookies}, CpS: {per_second}")
        return cookies, per_second
    
    def get_product_info(self) -> dict[Product, int]:
        prices = {}
        for product in Product:
            prices[product] = int(self.page.locator(f"#productPrice{product.value}").inner_text())
        return prices
        
    def buy_product(self, product: Product):
        self.page.locator(f"#product{product.value}").click()
        print(f"Bought {product}")

    def check_product_info(self):
        self.page.locator("div#product0").hover()
        self.read_tool_tip()
       
    def check_upgrades(self):
        #self.page.locator("div.upgrade")
        self.page.locator("div#upgrade0").hover()
        print(self.page.locator("#tooltipCrate").inner_html())

    def read_tool_tip(self):
        if self.page.query_selector('#tooltip'):
            print(self.page.locator("#tooltip").inner_html())
        else:
            print("Tooltip not found")





# div #tooltipCrate

# div#upgrades
# div#upgrade0


