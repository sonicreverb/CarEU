import multiprocessing
from mobile_scraper.parser import start_parser, start_activity_update
from mobile_scraper.database.database_main import update_tcalc


if __name__ == "__main__":
    parser_process = multiprocessing.Process(target=start_parser)
    activity_update_process = multiprocessing.Process(target=start_activity_update)
    tcalc_update_process = multiprocessing.Process(target=update_tcalc)

    parser_process.start()
    # tcalc_update_process.start()
    # activity_update_process.start()
