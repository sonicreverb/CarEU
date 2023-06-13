import os.path
import time
import ftplib

from selenium.webdriver.support.select import Select
from bs4 import BeautifulSoup
from main import BASE_DIR
from mobile_scraper.scraper_main import get_htmlsoup, get_data, create_driver
from mobile_scraper.database.database_main import write_productdata_to_db, get_local_links_from_db, \
    edit_product_activity_in_db, write_data_to_xlsx

HOST = "https://www.mobile.de"


def get_product_links_from_page(url):
    soup = get_htmlsoup(url)
    txt_name = "active_links.txt"

    # поиск и запись в массив всех ссылок на товары со страницы
    soup_a_li = soup.find_all('a', class_='vehicle-data track-event u-block js-track-event js-track-dealer-ratings')
    with open(os.path.join(BASE_DIR, "mobile_scraper", "links_data", txt_name), "a") as al_output:
        for link in soup_a_li:
            try:
                al_output.write(HOST + link.get('href') + "\n")
            except Exception as exc:
                print('error: links not found', exc)
    print("[GET ACTIVE LINKS INFO]", len(soup_a_li), url)

    # переход на следующую страницу
    if soup.find('a', class_='pagination-nav pagination-nav-right btn btn--muted btn--s'):
        try:
            get_product_links_from_page(HOST + soup.find('a', class_='pagination-nav pagination-nav-right btn '
                                                                     'btn--muted btn--s').get('href'))
        except Exception as exc:
            print('warning: next page link not found', exc)


def get_all_active_links(flag_upd_activity=False):
    if flag_upd_activity:
        txt_name = "activity_upd.txt"
    else:
        txt_name = "active_links.txt"

    # очистка содержимого active_links.txt
    with open(os.path.join(BASE_DIR, "mobile_scraper", "links_data", txt_name), "w"):
        pass

    with open(os.path.join(BASE_DIR, "mobile_scraper", "links_data", "filtered_links.txt")) as fl_input:
        for filtered_link in fl_input:
            get_product_links_from_page(filtered_link)


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


def update_products_activity(flag_upd_activity=False):
    if flag_upd_activity:
        txt_name = "activity_upd.txt"
    else:
        txt_name = "active_links.txt"

    # создаём множество ссылок на товары из таблицы
    local_links = get_local_links_from_db()
    if local_links:
        local_set = set(link for link in local_links)
        print(local_links[0:3])
        print("local set done")
    else:
        local_set = set()
        print("null local set done")

    # создаём множество актуальных ссылок на товары прямиком с mobile.de
    with open(os.path.join(BASE_DIR, "mobile_scraper", "links_data", txt_name), "r") as inp:
        active_li = []
        for line in inp:
            active_li.append(line.strip())
    active_set = set(active_li)
    print("active set done")

    # вычитаем множества и получаем ссылки, которые надо пометить неактивными в таблице +
    # необходимо спарсить и дозагрузить в таблице
    del_links = local_set - active_set
    upd_links = active_set - local_set
    print('total upd links: ', len(upd_links))

    # отмечаем неактивные товары в таблице
    for link in local_links:
        if link in del_links:
            edit_product_activity_in_db(link)

    return upd_links


# загрузка данных из БД на ftp
def upload_updtable_to_ftp():
    ftp_server = 'careu.ru'
    ftp_username = 'pikprice_123'
    ftp_password = 'u6M&k9J4'
    remote_file_path = 'output.xlsx'
    local_file_path = os.path.join(BASE_DIR, 'mobile_scraper', 'database', 'output.xlsx')

    # подключение к FTP серверу
    with ftplib.FTP(ftp_server, ftp_username, ftp_password) as ftp:
        print('[FTP INFO] Connecting to FTP server...')
        # открытие файла для чтения
        with open(local_file_path, 'rb') as file:
            # загрузка файла на сервер
            ftp.storbinary(f'STOR {remote_file_path}', file)
            print('[FTP INFO] Result table was uploaded successfully!')


def run_updater():
    # получаем ссылки для парсинга
    upd_links = update_products_activity()

    product_counter = 1

    for link in upd_links:
        try:
            # непосредственно парсинг товаров
            print(f"\n[UPDATER INFO] {product_counter}: {link}")
            product_data = get_data(link)

            if product_data:
                write_productdata_to_db(product_data)
                product_counter += 1

                # отправка данных на FTP сервер каждую тысячу товаров
                if product_counter % 100 == 0:
                    write_data_to_xlsx()
                    upload_updtable_to_ftp()

        except Exception as exc:
            print(exc, "in updater.py line 196")