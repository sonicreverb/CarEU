import datetime
from mobile_scraper.updater import get_all_active_links, update_products_activity
from mobile_scraper.database.database_main import update_tcalc, update_final_prices

while True:
    try:
        update_tcalc()
        print(f"\n[ACTIVITY UPDATER] Таможенный калькулятор успешно обновлен: {datetime.datetime.now()}")

        # update_final_prices()
        # print(f"\n[ACTIVITY UPDATER] Цены товаров успешно обновлены: {datetime.datetime.now()}")

        get_all_active_links(flag_upd_activity=True)
        update_products_activity(flag_upd_activity=True)

        print(f"[ACTIVITY UPDATER] Активность товаров успешно обновлена: {datetime.datetime.now()}")
    except Exception as _ex:
        print('[ACTIVITY UPDATER]', datetime.datetime.now(), _ex)