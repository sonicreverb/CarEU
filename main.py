import datetime

from mobile_scraper.database.database_main import upload_db_data_to_xlsx, update_tcalc, update_final_prices
from mobile_scraper.parser import start_parser, start_activity_update,  upload_db_to_ftp


if __name__ == "__main__":
    # start_activity_update()
    start_parser()
    update_final_prices()
    upload_db_data_to_xlsx()
    upload_db_to_ftp()
    print(datetime.datetime.now())
