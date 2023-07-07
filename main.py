import multiprocessing
from mobile_scraper.parser import start_parser, start_activity_validation, start_activity_update


if __name__ == "__main__":
    parser_process = multiprocessing.Process(target=start_parser)
    activity_update_process = multiprocessing.Process(target=start_activity_update)
    activity_validation_process = multiprocessing.Process(target=start_activity_validation)

    parser_process.start()
    activity_update_process.start()
    activity_validation_process.start()
