

from engine import CookieClicker, Product

engine = CookieClicker(headless=False)


while True:
    engine.click_big_cookie()
    cookies, per_second = engine.get_cookie_counts()
    prices = engine.get_product_info()

    if cookies >= prices[Product.Mine]:
        engine.buy_product(Product.Mine)
    elif cookies >= prices[Product.Farm]:
        engine.buy_product(Product.Farm)
    elif cookies >= prices[Product.Grandma]:
        engine.buy_product(Product.Grandma)
    elif cookies >= prices[Product.Cursor]:
        engine.buy_product(Product.Cursor)


