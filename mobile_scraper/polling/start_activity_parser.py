import datetime
from mobile_scraper.updater import get_all_active_links, update_products_activity

while True:
    try:
        get_all_active_links()
        update_products_activity()

        print(f"[ACTIVITY UPDATER] Активность товаров успешно обновлена: {datetime.datetime.now()}")
    except Exception as _ex:
        print('[ACTIVITY UPDATER]', datetime.datetime.now(), _ex)