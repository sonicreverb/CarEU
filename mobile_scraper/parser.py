import datetime
import os.path
import time
import ftplib
import threading

from selenium.webdriver.support.select import Select
from selenium.common.exceptions import InvalidSessionIdException, TimeoutException
from bs4 import BeautifulSoup
from mobile_scraper.scraper_main import get_htmlsoup, get_data, create_driver, kill_driver, reload_driver_proxy
from mobile_scraper.database.database_main import write_productdata_to_db, get_local_links_from_db, \
    get_active_names_from_db, edit_product_activity_in_db, get_unactive_links_from_db, \
    delete_unactive_positions
from mobile_scraper.telegram_alerts.telegram_notifier import send_notification

# BASE_DIR = os.path.dirname(os.path.dirname(__file__))
BASE_DIR = "C:\\Users\\careu\\PycharmProjects\\CarEU"
HOST = "https://www.mobile.de"
PARSING_TIME_DELAY = 0
driver_requests = 0


# возвращает все ссылки на товары со страницы
def get_product_links_from_page(driver):
    global driver_requests
    soup = get_htmlsoup(driver)
    driver_requests += 1
    txt_name = "active_links.txt"

    # поиск и запись в массив всех ссылок на товары со страницы
    soup_a_li = soup.find_all('a', class_='vehicle-data track-event u-block js-track-event js-track-dealer-ratings')
    with open(os.path.join(BASE_DIR, "mobile_scraper", "links_data", txt_name), "a") as al_output:
        for link in soup_a_li:
            try:
                al_output.write(HOST + link.get('href') + "\n")
            except Exception as exc:
                print('error: links not found', exc)
    print(f"({str(datetime.datetime.now())[:-7]}, {len(soup_a_li)})\n")

    # переход на следующую страницу
    if soup.find('a', class_='pagination-nav pagination-nav-right btn btn--muted btn--s'):
        try:
            # print(driver_requests)
            # if driver_requests % 10 == 0:
            #    driver = reload_driver_proxy(driver)

            new_url = HOST + soup.find('a', class_='pagination-nav pagination-nav-right btn '
                                                   'btn--muted btn--s').get('href')
            # переключаем вкладку
            print(f"[GET ACTIVE LINKS INFO] {new_url}")

            driver.execute_script('window.location.href = arguments[0];', new_url)
            # driver_requests += 1
            get_product_links_from_page(driver)

        except Exception as exc:
            print('warning: next page link not found', exc)


# итератор по ссылкам категорий для get_product_links_from_page
def get_all_active_links():
    txt_name = "active_links.txt"

    # очистка содержимого
    with open(os.path.join(BASE_DIR, "mobile_scraper", "links_data", txt_name), "w"):
        pass

    # создаём и открываем окно браузера
    with open(os.path.join(BASE_DIR, "mobile_scraper", "links_data", "filtered_links.txt")) as fl_input:
        for filtered_link in fl_input:
            try:
                driver = create_driver()
                driver = reload_driver_proxy(driver)
                driver.get('https://www.mobile.de/ru')

                print(f"[GET ACTIVE LINKS INFO] {filtered_link}", end="")
                driver.execute_script('window.location.href = arguments[0];', filtered_link)
                get_product_links_from_page(driver)
            except Exception as _ex:
                print('[GET ACTIVE LINKS INFO]', type(_ex), _ex)
            finally:
                kill_driver(driver)


def get_models_dict():
    start_link_to_scratch = 'https://www.mobile.de/ru/'
    soup = get_htmlsoup(start_link_to_scratch)
    make_list = soup.find_all('select', {'id': 'makeModelVariant1Make'})[0]
    make_list = make_list.find_all('option')

    upload_make = []
    upload_model = []
    upload_model_id = []
    upload_links = []

    for make in make_list:
        try:
            if make.get_text() in ['───────────────', 'Не важно', 'Другие']:
                continue
            # if make.get_text() == 'Abarth':
            #     break

            car_make = make.get_text()
            car_id = make.get('value')
            driver = create_driver()

            driver.get(start_link_to_scratch)
            time.sleep(3)

            driver.find_element('xpath', '//*[@id="mde-consent-modal-container"]/div[2]/div[2]/div[1]/button').click()
            Select(driver.find_element('xpath', '//*[@id="makeModelVariant1Make"]')).select_by_value(car_id)
            Select(driver.find_element('xpath', '//*[@id="minFirstRegistration"]')).select_by_value('2018')
            driver.find_element('xpath', '/html/body/div[1]/div/section[2]/div[2]/div/div[1]/form/div[4]/div[2]/input')\
                .click()
            time.sleep(3)

            base_source = driver.page_source
            base_soup = BeautifulSoup(base_source, 'html.parser')

            model_list = base_soup.findAll('div', {'class': 'form-group'})[1]
            models = model_list.findAll('option')

            models_names = []
            models_id = []

            for i in range(1, len(models)):
                if models[i].text.strip() not in ['Другие', 'Не важно']:
                    models_names.append(models[i].text.strip())
                    try:
                        models_id.append(models[i]['value'])
                    except Exception as exc:
                        models_id.append('')
                        print(exc, 'in links.py line 59')

            for value_index in range(len(models_id)):
                model_link = "https://suchen.mobile.de/fahrzeuge/search.html?dam=0&isSearchRequest=true&ms=" + \
                             car_id + ";" + models_id[value_index] + "&ref=quickSearch&sfmr=false&vc=Car"

                upload_make.append(car_make)
                upload_model.append(models_names[value_index])
                upload_model_id.append(models_id[value_index])
                upload_links.append(model_link)
        except Exception as exc:
            print(exc)

    return {"Producer": upload_make, "Models": upload_model, "ModelID": upload_model_id, "URL": upload_links}


# загрузка данных из таблицы на ftp
def upload_updtable_to_ftp(filename):
    ftp_server = 'ivvsavqz.beget.tech'
    ftp_username = 'ivvsavqz_2'
    ftp_password = 'xR*P4g7K'
    remote_file_path = filename
    local_file_path = os.path.join(BASE_DIR, 'mobile_scraper', 'database', remote_file_path)

    # подключение к FTP серверу
    with ftplib.FTP(ftp_server, ftp_username, ftp_password) as ftp:
        print('[FTP INFO] Connecting to FTP server...')
        # открытие файла для чтения
        with open(local_file_path, 'rb') as file:
            # загрузка файла на сервер
            ftp.storbinary(f'STOR {remote_file_path}', file)
            print('[FTP INFO] Result table was uploaded successfully!')


# загружает все пять таблиц output на сервер
def upload_db_to_ftp():
    upload_updtable_to_ftp('output1.xlsx')
    upload_updtable_to_ftp('output2.xlsx')
    upload_updtable_to_ftp('output3.xlsx')
    upload_updtable_to_ftp('output4.xlsx')
    upload_updtable_to_ftp('output5.xlsx')


# находит все индексы char, которые находятся в string
def find_all_indexes(string, char):
    indexes = []
    for i in range(len(string)):
        if string[i] == char:
            indexes.append(i)
    return indexes


# возвращает массив upd_links - уникальных ссылок для парсинга; если flag_upd_activity - отмечает неактиные ссылки в БД
def update_products_activity(to_del=False):
    txt_name = "active_links.txt"

    # создаём множество ссылок на товары из таблицы
    local_links = get_local_links_from_db()
    if local_links:
        short_links = []
        for link in local_links:
            ids = find_all_indexes(link, '/')
            short_links.append(link[:ids[5]])
        local_set = set(link for link in local_links)
        short_local_set = set(link for link in short_links)
        print(local_links[0:3])
        print("local set done")
    else:
        local_set = set()
        short_local_set = set()
        print("null local set done")

    # создаём множество актуальных ссылок на товары прямиком с mobile.de
    with open(os.path.join(BASE_DIR, "mobile_scraper", "links_data", txt_name), "r") as inp:
        active_li = []
        short_active_li = []
        for line in inp:
            ids = find_all_indexes(line.strip(), '/')
            short_active_li.append(line.strip()[:ids[5]])
            active_li.append(line.strip())
    active_set = set(active_li)
    short_active_set = set(short_active_li)
    print("active set done")

    # создаём множенство невалидных ссылок (не подходят под условие загрузки в бд <8 изображений и т.д)
    with open(os.path.join(BASE_DIR, "mobile_scraper", "links_data", 'invalid_links.txt'), "r") as inp:
        invalid_li = []
        for line in inp:
            invalid_li.append(line.strip())
    invalid_set = set(invalid_li)

    # вычитаем множества и получаем ссылки необходимо спарсить и дозагрузить в таблице
    upd_links = (active_set - local_set) - invalid_set
    print('total upd links: ', len(upd_links))

    # неактивные ссылки отмечаем... неактивными)
    if to_del:
        delete_links = short_local_set - short_active_set
        print(len(delete_links), delete_links)
        for idx in range(len(local_links)):
            for del_link in delete_links:
                if del_link + '/' in local_links[idx]:
                    edit_product_activity_in_db(local_links[idx])

    return upd_links


TIMEOUT_SECONDS = 120


# todo
# функция для запуска в отдельном потоке, которая проверяет находиться ли драйвер больше чем duration секунд
# на одной и той же странице, в случае если драйвер "завис" на одной и той же странице - вызывает driver.close()
def timeout_validation(driver, duration=TIMEOUT_SECONDS):
    old_url = driver.current_url
    time.sleep(duration)

    try:
        if driver.current_url == old_url:
            print(f'[TIMEOUT VALIDATION] ({threading.current_thread().name}) '
                  f'Driver was closed as the page processing time exceeded. ({old_url})')
            driver.refresh()

    except Exception as _ex:
        print(f'[TIMEOUT VALIDATION] ({threading.current_thread().name}) '
              f'Driver was closed because {_ex} ({old_url})')
        driver.refresh()


# запуск сессии парсинга
def start_parser():
    global driver_requests

    # формируем валидные ссылки для парсинга
    upd_links = update_products_activity()
    len_upd_links = len(upd_links)
    send_notification(f"[CAREU PARSER INFO] Кол-во позиций к парсингу: {len_upd_links}")

    success_counter = 1
    product_counter = 1

    # создаём и открываем окно браузера
    driver = create_driver()
    driver.get(HOST)
    for link in upd_links:
        try:
            driver_requests += 1
            if driver_requests % 50 == 0:
                driver = reload_driver_proxy(driver)
            # if product_counter % 50 == 0:
            #     kill_driver(driver)
            #     driver = create_driver()
            #     driver.get("https://duckduckgo.com/")
            if product_counter % 1000 == 0:
                send_notification(f"\n[CAREU PARSER INFO] Очередная тысяча товаров спрашена. "
                                  f"Текущее положение: {success_counter}/{len_upd_links}.")
            # отдельный поток для перехода на новый товар, если текущий обрабатывается уже более TIMEOUT_SECONDS
            # timeout_val_thread = threading.Thread(target=timeout_validation, name='TimeoutValidationThread',
            #                                       args=(driver, TIMEOUT_SECONDS))
            # timeout_val_thread.start()

            # непосредственно парсинг товаров
            print(f"\n[CAREU PARSER INFO] {success_counter}/{len_upd_links}. {link}")
            driver.execute_script('window.location.href = arguments[0];', link)
            soup = get_htmlsoup(driver)
            product_data = get_data(soup, link)
            active_names = get_active_names_from_db()

            # проверка на дубликат
            if product_data and (product_data['Title'] not in active_names):
                write_productdata_to_db(product_data)
                success_counter += 1

            else:
                len_upd_links -= 1
                invalid_links_file = open(os.path.join(BASE_DIR, 'mobile_scraper', 'links_data',
                                                       'invalid_links.txt'), 'a+', encoding='utf-8')
                invalid_links_file.write(link + "\n")
                invalid_links_file.close()

        except InvalidSessionIdException or TimeoutException:
            len_upd_links -= 1
            kill_driver(driver)
            print('[PARSING PROCESS] Driver timeout.')
            print('[PARSING RPOCESS] Recreating driver.')
            driver = create_driver()
            driver.get('https://duckduckgo.com')
        except Exception as _ex:
            print(_ex, "in updater.py line 196")
        time.sleep(PARSING_TIME_DELAY)
        product_counter += 1
    kill_driver(driver)


# поштучно проверяет активность спорных товаров на сайте по его ссылке
def start_activity_validation():
    links = get_unactive_links_from_db()
    total_links = len(links)
    cntr = 1

    # создаём и открываем окно браузера
    driver = create_driver()
    driver.get(HOST)
    for url in links:
        try:
            driver.execute_script('window.location.href = arguments[0];', url)
            soup = get_htmlsoup(driver)
            tag404 = soup.find('h1', text="Страница не найдена")

            if not tag404:
                edit_product_activity_in_db(url, True)
                print(f"[UNACTIVE LINKS VALIDATION] {cntr}/{total_links}. {not tag404} - {url}")

            else:
                edit_product_activity_in_db(url, unactivity_valid=True)
                print(f"[UNACTIVE LINKS VALIDATION] {cntr}/{total_links}. {not tag404} - {url}")

            cntr += 1
        except Exception as _ex:
            print(f"[UNACTIVE LINKS VALIDATION] Error: {_ex}")
        time.sleep(1)
    # delete_unactive_positions()
    kill_driver(driver)


# запускает сессию обновления активности товаров
def start_activity_update():
    get_all_active_links()
    update_products_activity(to_del=True)
    delete_unactive_positions()
    # start_activity_validation()

    print(f"\n[ACTIVITY UPDATER] Активность товаров успешна обновлена: {datetime.datetime.now()}")
