﻿import datetime
import os.path
import time
import ftplib

from selenium.webdriver.support.select import Select
from bs4 import BeautifulSoup
from mobile_scraper.scraper_main import get_htmlsoup, get_data, create_driver, kill_driver
from mobile_scraper.database.database_main import write_productdata_to_db, get_local_links_from_db, update_tcalc, \
    write_data_to_xlsx, get_active_names_from_db, edit_product_activity_in_db, get_unactive_links_from_db, \
    delete_unactive_positions

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
HOST = "https://www.mobile.de"


# возвращает все ссылки на товары со страницы
def get_product_links_from_page(driver, flag_upd_activity=False):
    soup = get_htmlsoup(driver)
    if flag_upd_activity:
        txt_name = 'upd_links.txt'
    else:
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
            new_url = HOST + soup.find('a', class_='pagination-nav pagination-nav-right btn '
                                                   'btn--muted btn--s').get('href')
            # переключаем вкладку
            print(f"[GET ACTIVE LINKS INFO] {new_url}")
            driver.execute_script('window.location.href = arguments[0];', new_url)
            get_product_links_from_page(driver, flag_upd_activity)

        except Exception as exc:
            print('warning: next page link not found', exc)


# итератор по ссылкам категорий для get_product_links_from_page
def get_all_active_links(flag_upd_activity=False):
    if flag_upd_activity:
        txt_name = 'upd_links.txt'
    else:
        txt_name = "active_links.txt"

    # очистка содержимого
    with open(os.path.join(BASE_DIR, "mobile_scraper", "links_data", txt_name), "w"):
        pass

    # создаём и открываем окно браузера
    driver = create_driver()
    driver.get('https://www.mobile.de/ru')
    with open(os.path.join(BASE_DIR, "mobile_scraper", "links_data", "filtered_links.txt")) as fl_input:
        for filtered_link in fl_input:
            try:
                print(f"[GET ACTIVE LINKS INFO] {filtered_link}", end="")
                driver.execute_script('window.location.href = arguments[0];', filtered_link)
                get_product_links_from_page(driver, flag_upd_activity)
            except Exception as _ex:
                print('[GET ACTIVE LINKS INFO]', _ex)
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


# загрузка данных из БД на ftp
def upload_updtable_to_ftp():
    ftp_server = 'careu.ru'
    ftp_username = 'pikprice_123'
    ftp_password = 'u6M&k9J4'
    remote_file_path = 'output.xlsx'
    local_file_path = os.path.join(BASE_DIR, 'mobile_scraper', 'database', remote_file_path)

    # подключение к FTP серверу
    with ftplib.FTP(ftp_server, ftp_username, ftp_password) as ftp:
        print('[FTP INFO] Connecting to FTP server...')
        # открытие файла для чтения
        with open(local_file_path, 'rb') as file:
            # загрузка файла на сервер
            ftp.storbinary(f'STOR {remote_file_path}', file)
            print('[FTP INFO] Result table was uploaded successfully!')


# находит все индексы char, которые находятся в string
def find_all_indexes(string, char):
    indexes = []
    for i in range(len(string)):
        if string[i] == char:
            indexes.append(i)
    return indexes


# возвращает массив upd_links - уникальных ссылок для парсинга; если flag_upd_activity - отмечает неактиные ссылки в БД
def update_products_activity(flag_upd_activity=False):
    if flag_upd_activity:
        txt_name = 'upd_links.txt'
    else:
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

    # вычитаем множества и получаем ссылки необходимо спарсить и дозагрузить в таблице
    upd_links = active_set - local_set
    print('total upd links: ', len(upd_links))

    # неактивные ссылки отмечаем... неактивными)
    if flag_upd_activity:
        delete_links = short_local_set - short_active_set
        print(len(delete_links), delete_links)
        for idx in range(len(local_links)):
            for del_link in delete_links:
                if del_link + '/' in local_links[idx]:
                    edit_product_activity_in_db(local_links[idx])

    return upd_links


# запуск сессии парсинга
def start_parser():
    while True:
        # парсим текущие активные ссылки товаров
        get_all_active_links()

        # формируем валидные ссылки для парсинга
        upd_links = update_products_activity()
        len_upd_links = len(upd_links)
        last_upd_time = time.time()
        product_counter = 1

        # создаём и открываем окно браузера
        driver = create_driver()
        driver.get(HOST)
        for link in upd_links:
            try:
                # непосредственно парсинг товаров
                print(f"\n[UPDATER INFO] {product_counter}/{len_upd_links}. {link}")
                driver.execute_script('window.location.href = arguments[0];', link)
                soup = get_htmlsoup(driver)
                product_data = get_data(soup, link)
                active_names = get_active_names_from_db()

                # проверка на дубликат
                if product_data and (product_data['Title'] not in active_names):
                    write_productdata_to_db(product_data)
                    product_counter += 1

                    # отправка данных на FTP сервер каждые 300 товаров, или по истечении двух часов
                    if product_counter % 300 == 0 or time.time() - last_upd_time > 7200:
                        last_upd_time = time.time()
                        write_data_to_xlsx()
                        upload_updtable_to_ftp()
            except Exception as _ex:
                print(_ex, "in updater.py line 196")

        kill_driver(driver)


# поштучно проверяет активность спорных товаров на сайте по его ссылке
def start_activity_validation():
    while True:
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
                    print(f"[UNACTIVE LINKS VALIDATION] {cntr}/{total_links}. {not tag404} - {url}")

                cntr += 1
            except Exception as _ex:
                print(f"[UNACTIVE LINKS VALIDATION] Error: {_ex}")
        delete_unactive_positions()
        kill_driver(driver)


# запускает сессию обновления активности товаров
def start_activity_update():
    while True:
        update_tcalc()
        print(f"\n[ACTIVITY UPDATER] Таможенный калькулятор успешно обновлен: {datetime.datetime.now()}")

        get_all_active_links(flag_upd_activity=True)
        update_products_activity(flag_upd_activity=True)
        print(f"\n[ACTIVITY UPDATER] Активность товаров успешна обновлена: {datetime.datetime.now()}")