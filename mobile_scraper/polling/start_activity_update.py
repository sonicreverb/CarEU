import datetime
from mobile_scraper.scraper_main import get_htmlsoup
from mobile_scraper.database.database_main import update_tcalc, edit_product_activity_in_db, get_active_links_from_db


# проверяет активность товара на сайте
def validate_link_activity(url):
    soup = get_htmlsoup(url)
    tag404 = soup.find('h1', string="Страница не найдена")

    if tag404:
        edit_product_activity_in_db(url)


# обновляет активность всех товаров в БД
def update_activity():
    active_li = get_active_links_from_db()
    for link in active_li:
        validate_link_activity(link)


while True:
    try:
        update_tcalc()
        print(f"\n[ACTIVITY UPDATER] Таможенный калькулятор успешно обновлен: {datetime.datetime.now()}")

        update_activity()
        print(f"[ACTIVITY UPDATER] Активность товаров успешно обновлена: {datetime.datetime.now()}")
    except Exception as _ex:
        print('[ACTIVITY UPDATER]', datetime.datetime.now(), _ex)
