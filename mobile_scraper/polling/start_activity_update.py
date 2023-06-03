import datetime
from mobile_scraper.updater import get_all_active_links, update_products_activity, get_htmlsoup
from mobile_scraper.database.database_main import update_tcalc, edit_product_activity_in_db, \
    get_unactive_links_for_validation


# проверяет активность товара на сайте
def validate_link_activity(url):
    soup = get_htmlsoup(url)
    tag404 = soup.find('h1', string="Страница не найдена")

    if tag404:
        edit_product_activity_in_db(url, "NonActive")
    else:
        edit_product_activity_in_db(url, "Active")


# обновляет активность всех товаров в БД
def validate_activity():
    active_li = get_unactive_links_for_validation()
    print(f'[LINKS UPD ACTIVITY] - {len(active_li)}')
    cntr = 1
    for link in active_li:
        print(f'[LINKS UPD ACTIVITY] - {cntr}: {link}')
        validate_link_activity(link)
        cntr += 1


while True:
    try:
        update_tcalc()
        print(f"\n[ACTIVITY UPDATER] Таможенный калькулятор успешно обновлен: {datetime.datetime.now()}")

        get_all_active_links(flag_upd_activity=True)
        update_products_activity(flag_upd_activity=True)
        validate_activity()

        print(f"[ACTIVITY UPDATER] Активность товаров успешно обновлена: {datetime.datetime.now()}")
    except Exception as _ex:
        print('[ACTIVITY UPDATER]', datetime.datetime.now(), _ex)
