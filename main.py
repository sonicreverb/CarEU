import datetime
import time
import os

from mobile_scraper.database.database_main import upload_db_data_to_xlsx, update_tcalc, update_final_prices # clear_duples_and_out_of_date_prods
from mobile_scraper.parser import start_parser, start_activity_update, upload_db_to_ftp
from mobile_scraper.telegram_alerts.telegram_notifier import send_notification

DEBUG = True


if __name__ == "__main__":
    try:
        begin_time = time.time()

        send_notification(f"[CAREU] Запущен процесс обновления активности товаров "
                          f"({str(datetime.datetime.now())[:-7]}).")
        start_activity_update()
        send_notification(f"[CAREU] Процесс обновления активности товаров завершён "
                          f"({str(datetime.datetime.now())[:-7]}).")

        send_notification(f"[CAREU] Запущен процесс парсинга товаров ({str(datetime.datetime.now())[:-7]}).")
        start_parser()
        send_notification(f"[CAREU] Процесс парсинга товаров завершён ({str(datetime.datetime.now())[:-7]}).")

        last_request_time = time.time()
        send_notification(f"[CAREU] Обновление таможенного калькулятора и акутальных цен "
                          f"({str(datetime.datetime.now())[:-7]}).")
        update_tcalc()
        update_final_prices()
        # clear_duples_and_out_of_date_prods()

        send_notification(f"[CAREU] Загрузка данных в таблицы ({str(datetime.datetime.now())[:-7]}).)")
        upload_db_data_to_xlsx()

        send_notification(f"[CAREU] Загрузка данных на FTP ({str(datetime.datetime.now())[:-7]}).")
        upload_db_to_ftp()

        if time.time() - last_request_time < 3600:
            send_notification(f"[CAREU] ({str(datetime.datetime.now())[:-7]}) Сессия завершена за "
                              f"{str(int(time.time() - begin_time) / 3600)[:3]} ч. "
                              f"Время ожидания {int(int(time.time() - last_request_time) / 60)} м.")
            time.sleep(time.time() - last_request_time)
        else:
            send_notification(f"[CAREU] ({str(datetime.datetime.now())[:-7]}) Сессия завершена за "
                              f"{str(int(time.time() - begin_time) / 3600)[:3]} ч. "
                              f"Время ожидания 0 м.")

    except Exception as _exception:
        send_notification(f"[CAREU] Во время сессии возникла ошибка ({str(datetime.datetime.now())[:-7]}).\n"
                          f"Информация об ошибке: {_exception}")
        if not DEBUG:
            os.system('shutdown -r -t 30')
    finally:
        if not DEBUG:
            os.system('shutdown -r -t 30')
