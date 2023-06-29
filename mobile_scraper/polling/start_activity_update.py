import datetime
from mobile_scraper.updater import get_htmlsoup
from mobile_scraper.database.database_main import update_tcalc, edit_product_activity_in_db, get_active_links_from_db


# проверяет активность товара на сайте
def validate_link_activity(url):
    soup = get_htmlsoup(url)
    tag404 = soup.find('h1', string="Страница не найдена")

    if tag404:
        edit_product_activity_in_db(url)
        return False

    return True


# обновляет активность всех товаров в БД
def update_product_activity():
    update_tcalc()
    print(f"\n[ACTIVITY UPDATER] Таможенный калькулятор успешно обновлен: {datetime.datetime.now()}")

    links = get_active_links_from_db()
    print(f'[LINKS UPD ACTIVITY] TOTAL LINKS: {len(links)}')
    cntr = 1
    for link in links:
        try:
            activity_status = validate_link_activity(link)
            print(f'[LINKS UPD ACTIVITY] {cntr}. Activity - {activity_status} {link}')
            cntr += 1

            if cntr % 50 == 0:
                update_tcalc()
                print(f"\n[ACTIVITY UPDATER] Таможенный калькулятор успешно обновлен: {datetime.datetime.now()}")

        except Exception as _ex:
            print('[ACTIVITY UPDATER]', datetime.datetime.now(), _ex)

    print(f"[ACTIVITY UPDATER] Активность товаров успешно обновлена: {datetime.datetime.now()}")


while True:
    update_product_activity()
