

from engine import CookieClicker, Product

engine = CookieClicker(headless=True)


#while True:
for _ in range(200):
    engine.click_big_cookie()
    cookies, per_second = engine.get_cookie_counts()
    #prices = engine.get_product_info()
    # if cookies >= prices[Product.Cursor]:
    #     engine.buy_product(Product.Cursor)

engine.check_product_info()
engine.buy_product(Product.Cursor)
engine.click_big_cookie()
#engine.check_upgrades()

engine.check_product_info()

