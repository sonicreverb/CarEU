from mobile_scraper.updater import update_products_activity
import datetime


while True:
    try:
        update_products_activity()

        print(f"Активность товаров успешно обновлена: {datetime.datetime.now()}")
    except Exception as exc:
        print(exc, datetime.datetime.now())
