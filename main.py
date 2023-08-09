import datetime
import time

from mobile_scraper.database.database_main import upload_db_data_to_xlsx, update_tcalc, update_final_prices
from mobile_scraper.parser import start_parser, start_activity_update, upload_db_to_ftp
from mobile_scraper.telegram_alerts.telegram_notifier import send_notification

if __name__ == "__main__":
    while True:
        try:
            begin_time = time.time()

            send_notification(f"[CAREU] Запущен процесс обновления актинвости товаров ({datetime.datetime.now()}).")
            start_activity_update()
            send_notification(f"[CAREU] Процесс обновления актинвости товаров завершён ({datetime.datetime.now()}).)")

            send_notification(f"[CAREU] Запущен процесс парсинга товаров ({datetime.datetime.now()}).")
            start_parser()
            send_notification(f"[CAREU] Процесс парсинга товаров завершён ({datetime.datetime.now()}).)")

            last_request_time = time.time()
            send_notification(f"[CAREU] Обновление таможенного калькулятора и акутальных цен "
                              f"({datetime.datetime.now()}).)")
            update_tcalc()
            update_final_prices()

            send_notification(f"[CAREU] Загрузка данных в таблицы ({datetime.datetime.now()}).)")
            upload_db_data_to_xlsx()

            send_notification(f"[CAREU] Загрузка данных на FTP ({datetime.datetime.now()}).)")
            upload_db_to_ftp()

            if time.time() - last_request_time < 3600:
                send_notification(f"[CAREU] ({datetime.datetime.now()}) Сессия завершена за "
                                  f"{int(time.time() - begin_time) / 3600} ч. "
                                  f"Время ожидания {int(time.time() - last_request_time) / 60} м.")
                time.sleep(time.time() - last_request_time)
            else:
                send_notification(f"[CAREU] ({datetime.datetime.now()}) Сессия завершена за "
                                  f"{int(time.time() - begin_time) / 3600} ч. "
                                  f"Время ожидания 0 м.")

        except Exception as _exception:
            send_notification(f"[CAREU] Во время сессии возникла ошибка ({datetime.datetime.now()}).\n"
                              f"Информация об ошибке: {_exception}")
            break
