
import re
import time
from enum import Enum
from collections import defaultdict

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError



COOKIE_COUNT_REGEX = r"(?P<cookies>[0-9,]+(\.[0-9]+)?( million)?( billion)?) cookies? per second: (?P<cps>[0-9,]+(\.[0-9]+)?( million)?( billion)?)"

PRODUCT_TOOLTIP_REGEX = r"^(?P<price>[0-9,]+(\.[0-9]+)?( million)?( billion)?) (?P<product>.+) owned: (?P<owned>[0-9,]+) .+\. each .+ produces (?P<cps>[0-9,]+(\.[0-9]+)?( million)?( billion)?) cookies? per second .+$"

UPGRADE_TOOLTIP_REGEX = r"^(?P<price>[0-9,]+(\.[0-9]+)?( million)?( billion)?) (?P<upgrade>.+)$"



class Product(Enum):
    Cursor = 0
    Grandma = 1
    Farm = 2
    Mine = 3
    Factory = 4
    Bank = 5
    Temple = 6
    WizardTower = 7

def _parse_float(str_value) -> float:
    multiplier = 1
    if ' million' in str_value:
        str_value = str_value.replace(' million', '')
        multiplier = 1_000_000
    if ' billion' in str_value:
        str_value = str_value.replace(' billion', '')
        multiplier = 1_000_000_000
    return float(str_value.replace(',', ''))*multiplier

class CookieClicker():
    def __init__(self, *, headless: bool = False):
        self._playwright = sync_playwright().start()
        self._browser = None
        self._context = None
        self.page = None
        self._start(headless)

    def _start(self, headless: bool):
        print("Starting browser")
        self._browser = self._playwright.chromium.launch(
            headless=headless, args=["--start-maximized"])
        self._context = self._browser.new_context(no_viewport=True)
        self.page = self._context.new_page()
        print("Navigating to cookie clicker")
        self.page.goto("https://orteil.dashnet.org/cookieclicker/")
        print("Consent to cookies and select langauage")
        self.page.get_by_role("button", name="Consent").click()
        self.page.locator("#langSelect-EN").click()
        print("Game ready")

    def click_big_cookie(self):
        self.page.locator("#bigCookie").click()

    def get_cookie_counts(self) -> tuple[int, int]:
        cookies, cps = 0, 0
        cookie_counts_text = self.page.locator("#cookies").inner_text().replace('\n', ' ')
        result = re.match(COOKIE_COUNT_REGEX, cookie_counts_text)
        if result:
            cookies = _parse_float(result.group('cookies'))
            cps = _parse_float(result.group('cps'))
        #print(f"Cookies: {cookies}, CpS: {cps}")
        return cookies, cps

    def get_product_info(self) -> dict[Product, int]:
        info = defaultdict(lambda: {})
        previous_cps = 0
        for product in Product:
            info[product]['product'] = product
            price_string = self.page.locator(f"#productPrice{product.value}").inner_text()
            info[product]['price'] = _parse_float(price_string)
            if info[product]['price']:
                tooltip_data = self.get_product_tooltip_data(product)
                info[product]['owned'] = tooltip_data.get('owned', 0)
                info[product]['cps'] = tooltip_data.get('cps', 0)
                info[product]['cpspc'] = (info[product]['cps'] or previous_cps)/info[product]['price']
                previous_cps = info[product]['cps']
        return info

    def get_product_tooltip_data(self, product) -> dict:
        try:
            self.page.locator(f"div#product{product.value}").hover(timeout=100)
            return self._parse_product_tooltip(self.read_tooltip_text())
        except PlaywrightTimeoutError:
            pass
        return {}

    def buy_product(self, product: Product):
        self.page.locator(f"#product{product.value}").click()
        #print(f"Bought {product}")

    def _parse_product_tooltip(self, tooltip_string) -> dict:
        if not tooltip_string:
            return {}
        tooltip_string = tooltip_string.replace('\n', ' ')
        # print('----------------')
        # print(tooltip_string)
        result = re.match(PRODUCT_TOOLTIP_REGEX, tooltip_string)
        # print(result.groups() if result else None)
        # print('----------------')
        if not result:
            return {}
        return {
            'price': _parse_float(result.group('price')),
            'owned': _parse_float(result.group('owned')),
            'cps': _parse_float(result.group('cps')),
        }

    def read_tooltip_text(self) -> str:
        if self.page.query_selector('#tooltip'):
            string = self.page.locator("#tooltip").inner_text()
            return string
        print("Tooltip not found")
        return None

    def get_updagrade_info(self) -> list[dict]:
        upgrades = []
        for index in range(3):
            if not self.page.query_selector(f"div#upgrade{index}"):
                continue
            self.page.locator(f"div#upgrade{index}").hover()
            text = self._read_tooltip_crate()
            upgrade = self._parse_upgrade_tooltip(text)
            upgrade['index'] = index
            upgrades.append(upgrade)
        return upgrades

    def _read_tooltip_crate(self):
        if self.page.query_selector('#tooltipCrate'):
            return self.page.locator("#tooltipCrate").inner_text()
        print("TooltipCrate not found")
        return None

    def _parse_upgrade_tooltip(self, tooltip_string) -> dict:
        if not tooltip_string:
            return {}
        tooltip_string = tooltip_string.replace('\n', ' ')
        result = re.match(UPGRADE_TOOLTIP_REGEX, tooltip_string)
        if not result:
            print('Unable to parse:')
            print(tooltip_string)
            return {}
        return {
            'price': _parse_float(result.group('price')),
            'upgrade': result.group('upgrade'),
        }

    def buy_upgrade(self, index):
        print("Buying upgrade")
        self.page.locator(f"div#upgrade{index}").hover()
        text = self.page.locator("#tooltipCrate").inner_text()
        print(text.replace('\n', ' '))
        self.page.locator(f"div#upgrade{index}").click()


    def measure_active_clicking(self, *, minimum_cookies: int = 100, minimum_time: float = 3) -> float:
        original_cookies, original_cps = self.get_cookie_counts()
        cookies = original_cookies
        start = time.time()
        while cookies - original_cookies < minimum_cookies or time.time() - start < minimum_time:
            self.click_big_cookie()
            cookies, _ = self.get_cookie_counts()
        total_cps = (cookies - original_cookies)/(time.time() - start)
        active_cps = total_cps - original_cps
        print(f"Active click speed: {active_cps} cps")
        return active_cps
