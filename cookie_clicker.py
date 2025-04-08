
import time

from engine import CookieClicker, Product

engine = CookieClicker(headless=False)



def select_next_product(product_info, base_cps) -> Product:
    for product in product_info:
        product_info[product]['time_required'] = product_info[product]['price']/base_cps
        advantage_point = product_info[product]['time_required']
        if product_info[product]['cps']:
            advantage_point = product_info[product]['price'] * (base_cps + product_info[product]['cps']) / (base_cps*product_info[product]['cps'])
        product_info[product]['advantage_point'] = advantage_point
    best_product = sorted(list(product_info.values()), key=lambda x: x['advantage_point'])[0]
    print('Next product:', best_product['product'], best_product['price'], best_product['time_required'], 'sec')
    return best_product['product']

def select_next_upgrade(upgrades) -> str:
    if upgrades:
        print('Next upgrade:', upgrades[0]['price'], upgrades[0]['upgrade'])
        if not upgrades[0].get('price', None):
            return None
        return upgrades[0]['index']
    return None


def main():
    active_cps = engine.measure_active_clicking()

    next_product = None
    next_upgrade = None
    product_info = {}
    upgrades = []
    while True:
        cookies, cps = engine.get_cookie_counts()
        if active_cps > 0.0001*cps:
            engine.click_big_cookie()
        else:
            active_cps = 0

        if next_upgrade is None:
            upgrades = engine.get_updagrade_info()
            next_upgrade = select_next_upgrade(upgrades)

        if next_upgrade is not None and upgrades[next_upgrade]['price'] <= cookies:
            engine.buy_upgrade(next_upgrade)
            next_product = None
            next_upgrade = None

        if not next_product:
            product_info = engine.get_product_info()
            next_product = select_next_product(product_info, cps + active_cps)

        if next_product and product_info[next_product]['price'] <= cookies:
            engine.buy_product(next_product)
            next_product = None
            next_upgrade = None



if __name__ == '__main__':
    main()
