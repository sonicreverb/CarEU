import datetime
from mobile_scraper.updater import get_all_active_links, update_products_activity
from mobile_scraper.database.database_main import update_tcalc, edit_product_activity_in_db, get_unactive_links_from_db
from mobile_scraper.scraper_main import get_htmlsoup


# поштучно проверяет активность спорных товаров на сайте по его ссылке
def validate_links_activity():
    links = get_unactive_links_from_db()
    total_links = len(links)
    cntr = 1
    for url in links:
        try:
            soup = get_htmlsoup(url)
            tag404 = soup.find('h1', text="Страница не найдена")

            if not tag404:
                edit_product_activity_in_db(url, True)
                print(f"[UNACTIVE LINKS VALIDATION] {cntr}/{total_links}. {not tag404} - {url}")

            else:
                print(f"[UNACTIVE LINKS VALIDATION] {cntr}/{total_links}. {not tag404} - {url}")

            cntr += 1
        except Exception as _ex:
            print(f"[UNACTIVE LINKS VALIDATION] Error: {_ex}")


while True:
    update_tcalc()
    print(f"\n[ACTIVITY UPDATER] Таможенный калькулятор успешно обновлен: {datetime.datetime.now()}")

    get_all_active_links(flag_upd_activity=True)
    update_products_activity(flag_upd_activity=True)
    # validate_links_activity()
    print(f"\n[ACTIVITY UPDATER] Активность товаров успешна обновлена: {datetime.datetime.now()}")
