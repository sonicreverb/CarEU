import datetime
import time

from mobile_scraper.database.database_main import upload_db_data_to_xlsx, update_tcalc, update_final_prices
from mobile_scraper.parser import start_parser, start_activity_update,  upload_db_to_ftp


if __name__ == "__main__":
    begin_time = time.time()
    start_activity_update()
    start_parser()
    last_request_time = time.time()
    update_final_prices()
    upload_db_data_to_xlsx()
    upload_db_to_ftp()

    if time.time() - last_request_time < 3600:
        print(f"[MAIN PROCESS] ({datetime.datetime.now()}) Сессия завершена за {time.time() - begin_time}."
              f" Время ожидания {time.time() - last_request_time} ")
        time.sleep(time.time() - last_request_time)
