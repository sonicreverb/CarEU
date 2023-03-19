import json
import os.path
import time

from main import BASE_DIR
from mobile_scraper.scraper_main import get_htmlsoup, get_data
from mobile_scraper.GoogleSheets.gsheets import read_column, write_column, get_last_row
from mobile_scraper.links import read_mark_models
from mobile_scraper.proxy.proxy_manager import PROXY_FILENAMES, set_proxy, remove_proxy

HOST = "https://www.mobile.de"


def get_product_links_from_page(url):
    soup = get_htmlsoup(url)

    # поиск и запись в массив всех ссылок на товары со страницы
    soup_a_li = soup.find_all('a', class_='vehicle-data track-event u-block js-track-event js-track-dealer-ratings')
    with open(os.path.join(BASE_DIR, "mobile_scraper", "data", "active_links.txt"), "a") as al_output:
        for link in soup_a_li:
            try:
                al_output.write(HOST + link.get('href') + "\n")
            except Exception as exc:
                print('error: links not found', exc)
    print(len(soup_a_li), url)

    # переход на следующую страницу
    if soup.find('a', class_='pagination-nav pagination-nav-right btn btn--muted btn--s'):
        try:
            get_product_links_from_page(HOST + soup.find('a', class_='pagination-nav pagination-nav-right btn '
                                                                     'btn--muted btn--s').get('href'))
        except Exception as exc:
            print('warning: next page link not found', exc)


def get_all_active_links():
    # очистка содержимого active_links.txt
    with open(os.path.join(BASE_DIR, "mobile_scraper", "data", "active_links.txt"), "w"):
        pass

    with open(os.path.join(BASE_DIR, "mobile_scraper", "data", "filtered_links.txt")) as fl_input:
        iteration_counter = 0
        proxy_id = 0
        # переменная для удаления прокси в самом конце работы программы
        last_used_proxy_id = 0

        for filtered_link in fl_input:
            # если прокси уже было установлено, то есть это не первый запрос - удаляем его
            if iteration_counter != 0:
                remove_proxy(PROXY_FILENAMES[proxy_id])
            set_proxy(PROXY_FILENAMES[proxy_id])
            last_used_proxy_id = proxy_id

            print(f'used proxy - {PROXY_FILENAMES[proxy_id - 1]}')
            get_product_links_from_page(filtered_link)
            iteration_counter += 1

        # избавляемся от прокси в конце выполнения парсинга
        remove_proxy(last_used_proxy_id)


def get_local_links():
    return read_column('D', 'data')


def upload_data_to_sheets():
    with open(os.path.join(BASE_DIR, 'mobile_scraper', 'data', 'products_json.txt')) as input_file:
        data = json.load(input_file)
        products = data['products']

        # каждый столбец, который будет записан - массив, думаю, что найдётся способ это оптимизировать, а пока todo
        upload_products_names = []
        upload_products_models = []
        upload_products_makes = []
        upload_products_urls = []
        upload_products_prices_brutto = []
        upload_products_prices_netto = []
        upload_products_charachteristics = []
        upload_products_descriptions = []
        upload_products_dealername = []
        upload_products_dealersite = []
        upload_products_dealerphonenumber = []

        upload_products_img1 = []
        upload_products_img2 = []
        upload_products_img3 = []
        upload_products_img4 = []
        upload_products_img5 = []
        upload_products_img6 = []
        upload_products_img7 = []
        upload_products_img8 = []
        upload_products_img9 = []
        upload_products_img10 = []
        upload_products_img11 = []
        upload_products_img12 = []
        upload_products_img13 = []
        upload_products_img14 = []
        upload_products_img15 = []

        upload_products_category1 = []
        upload_products_category2 = []
        upload_products_category3 = []
        upload_products_category4 = []
        upload_products_category5 = []
        upload_products_category6 = []
        upload_products_category7 = []
        upload_products_category8 = []
        upload_products_category9 = []
        upload_products_category10 = []
        upload_products_category11 = []
        upload_products_category12 = []
        upload_products_category13 = []
        upload_products_category14 = []
        upload_products_category15 = []
        upload_products_category16 = []
        upload_products_category17 = []
        upload_products_category18 = []
        upload_products_category19 = []
        upload_products_category20 = []
        upload_products_category21 = []
        upload_products_category22 = []
        upload_products_category23 = []
        upload_products_category24 = []

        upload_data = [upload_products_names,
                       upload_products_makes,
                       upload_products_models,
                       upload_products_urls,
                       upload_products_prices_brutto,
                       upload_products_prices_netto,
                       upload_products_charachteristics,
                       upload_products_descriptions,
                       upload_products_dealername,
                       upload_products_dealersite,
                       upload_products_dealerphonenumber,

                       upload_products_img1,
                       upload_products_img2,
                       upload_products_img3,
                       upload_products_img4,
                       upload_products_img5,
                       upload_products_img6,
                       upload_products_img7,
                       upload_products_img8,
                       upload_products_img9,
                       upload_products_img10,
                       upload_products_img11,
                       upload_products_img12,
                       upload_products_img13,
                       upload_products_img14,
                       upload_products_img15,

                       upload_products_category1,
                       upload_products_category2,
                       upload_products_category3,
                       upload_products_category4,
                       upload_products_category5,
                       upload_products_category6,
                       upload_products_category7,
                       upload_products_category8,
                       upload_products_category9,
                       upload_products_category10,
                       upload_products_category11,
                       upload_products_category12,
                       upload_products_category13,
                       upload_products_category14,
                       upload_products_category15,
                       upload_products_category16,
                       upload_products_category17,
                       upload_products_category18,
                       upload_products_category19,
                       upload_products_category20,
                       upload_products_category21,
                       upload_products_category22,
                       upload_products_category23,
                       upload_products_category24, ]

        # переменная объявлена сейчас, чтобы далее в цикле каждый раз не вызывать get_last_row
        last_row = str(get_last_row('data') + 1)

        # словарь моделей имеющихся марок
        all_models_dict = read_mark_models()

        for product in products:
            if product:
                upload_products_names.append([product['Title']])

                # информация о марках и моделях
                product_make = ' '
                product_model = ' '

                for make in all_models_dict:
                    if make in product['Title']:
                        product_make = make
                        for model in all_models_dict[make]:
                            if model in product['Title']:
                                product_model = model

                upload_products_makes.append([product_make])
                upload_products_models.append([product_model])

                upload_products_urls.append([product['URL']])
                upload_products_prices_brutto.append([int(product['BruttoPrice'])])
                upload_products_prices_netto.append([int(product['NettoPrice'])])
                upload_products_charachteristics.append([product['CharacteristicsStr']])
                upload_products_descriptions.append([product['DescriptionStr']])

                try:
                    if product['DealerData'][0] != "Связаться с продавцом":
                        upload_products_dealername.append([product['DealerData'][0]])
                    else:
                        upload_products_dealername.append([' '])
                    if product['DealerData'][1] != "#contact-seller":
                        upload_products_dealersite.append([product['DealerData'][1]])
                    else:
                        upload_products_dealersite.append([' '])
                    upload_products_dealerphonenumber.append([product['DealerData'][2]])
                except Exception as exc:
                    print(exc)
                    upload_products_dealername.append([' '])
                    upload_products_dealersite.append([' '])
                    upload_products_dealerphonenumber.append([' '])

                # todo IMGLI
                if len(product['ImgLi']) >= 1:
                    upload_products_img1.append([product['ImgLi'][0]])
                else:
                    upload_products_img1.append([' '])
                if len(product['ImgLi']) >= 2:
                    upload_products_img2.append([product['ImgLi'][1]])
                else:
                    upload_products_img2.append([' '])
                if len(product['ImgLi']) >= 3:
                    upload_products_img3.append([product['ImgLi'][2]])
                else:
                    upload_products_img3.append([' '])
                if len(product['ImgLi']) >= 4:
                    upload_products_img4.append([product['ImgLi'][3]])
                else:
                    upload_products_img4.append([' '])
                if len(product['ImgLi']) >= 5:
                    upload_products_img5.append([product['ImgLi'][4]])
                else:
                    upload_products_img5.append([' '])
                if len(product['ImgLi']) >= 6:
                    upload_products_img6.append([product['ImgLi'][5]])
                else:
                    upload_products_img6.append([' '])
                if len(product['ImgLi']) >= 7:
                    upload_products_img7.append([product['ImgLi'][6]])
                else:
                    upload_products_img7.append([' '])
                if len(product['ImgLi']) >= 8:
                    upload_products_img8.append([product['ImgLi'][7]])
                else:
                    upload_products_img8.append([' '])
                if len(product['ImgLi']) >= 9:
                    upload_products_img9.append([product['ImgLi'][8]])
                else:
                    upload_products_img9.append([' '])
                if len(product['ImgLi']) >= 10:
                    upload_products_img10.append([product['ImgLi'][9]])
                else:
                    upload_products_img10.append([' '])
                if len(product['ImgLi']) >= 11:
                    upload_products_img11.append([product['ImgLi'][10]])
                else:
                    upload_products_img11.append([' '])
                if len(product['ImgLi']) >= 12:
                    upload_products_img12.append([product['ImgLi'][11]])
                else:
                    upload_products_img12.append([' '])
                if len(product['ImgLi']) >= 13:
                    upload_products_img13.append([product['ImgLi'][12]])
                else:
                    upload_products_img13.append([' '])
                if len(product['ImgLi']) >= 14:
                    upload_products_img14.append([product['ImgLi'][13]])
                else:
                    upload_products_img14.append([' '])
                if len(product['ImgLi']) >= 15:
                    upload_products_img15.append([product['ImgLi'][14]])
                else:
                    upload_products_img15.append([' '])

                # todo CATEGORIES
                techopt = product['TechOptDict']

                if 'Категория' in techopt:
                    upload_products_category1.append([techopt['Категория']])
                else:
                    upload_products_category1.append([''])
                if 'Первая регистрация' in techopt:
                    upload_products_category2.append([techopt['Первая регистрация']])
                else:
                    upload_products_category2.append([''])
                if 'Коробка передач' in techopt:
                    upload_products_category3.append([techopt['Коробка передач']])
                else:
                    upload_products_category3.append([''])
                if 'Топливо' in techopt:
                    upload_products_category4.append([techopt['Топливо']])
                else:
                    upload_products_category4.append([''])
                if 'Пробег' in techopt:
                    upload_products_category5.append([techopt['Пробег']])
                else:
                    upload_products_category5.append([''])
                if 'Мощность' in techopt:
                    upload_products_category6.append([techopt['Мощность']])
                else:
                    upload_products_category6.append([''])
                if 'Объем двигателя' in techopt:
                    upload_products_category7.append([techopt['Объем двигателя']])
                else:
                    upload_products_category7.append([''])
                if 'Количество мест' in techopt:
                    upload_products_category8.append([techopt['Количество мест']])
                else:
                    upload_products_category8.append([''])
                if 'Число дверей' in techopt:
                    upload_products_category9.append([techopt['Число дверей']])
                else:
                    upload_products_category9.append([''])
                if 'Класс экологической безопасности' in techopt:
                    upload_products_category10.append([techopt['Класс экологической безопасности']])
                else:
                    upload_products_category10.append([''])
                if 'Количество владельцев транспортного средства' in techopt:
                    upload_products_category11.append([techopt['Количество владельцев транспортного средства']])
                else:
                    upload_products_category11.append([''])
                if 'Общий осмотр' in techopt:
                    upload_products_category12.append([techopt['Общий осмотр']])
                else:
                    upload_products_category12.append([''])
                if 'Цвет' in techopt:
                    upload_products_category13.append([techopt['Цвет']])
                else:
                    upload_products_category13.append([''])
                if 'Цвет по классификации производителя' in techopt:
                    upload_products_category14.append([techopt['Цвет по классификации производителя']])
                else:
                    upload_products_category14.append([''])
                if 'Состояние транспортного средства' in techopt:
                    upload_products_category15.append([techopt['Состояние транспортного средства']])
                else:
                    upload_products_category15.append([''])
                if 'Оригинал' in techopt:
                    upload_products_category16.append([techopt['Оригинал']])
                else:
                    upload_products_category16.append([''])
                if 'Потребление' in techopt:
                    upload_products_category17.append([techopt['Потребление']])
                else:
                    upload_products_category17.append([''])
                if 'CO₂ Emissions' in techopt:
                    upload_products_category18.append([techopt['CO₂ Emissions']])
                else:
                    upload_products_category18.append([''])
                if 'Датчики парковки' in techopt:
                    upload_products_category19.append([techopt['Датчики парковки']])
                else:
                    upload_products_category19.append([''])
                if 'Дизайн салона' in techopt:
                    upload_products_category20.append([techopt['Дизайн салона']])
                else:
                    upload_products_category20.append([''])
                if 'Номер транспортного средства' in techopt:
                    upload_products_category21.append([techopt['Номер транспортного средства']])
                else:
                    upload_products_category21.append([''])
                if 'Наличие' in techopt:
                    upload_products_category22.append([techopt['Наличие']])
                else:
                    upload_products_category22.append([''])
                if 'Вид основного топлива' in techopt:
                    upload_products_category23.append([techopt['Вид основного топлива']])
                else:
                    upload_products_category23.append([''])

            # непосредственно запись в таблицу, каждый массив - столбец в таблице

        for row_index in range(len(upload_data)):
            # 26 - кол-во букв в англ. алфавите, 65 - константа для преобразований числового индекса через ascii
            # в название столбца
            if row_index < 26:
                row_name = chr(row_index + 65)
            else:
                row_name = 'A' + chr(row_index - 26 + 65)

        writing_range = row_name + last_row + ':' + row_name
        write_column(upload_data[row_index], writing_range)
        time.sleep(5)


def run_updater():
    # создаём множество ссылок на товары из таблицы
    local_links = get_local_links()
    local_set = set(link for link in local_links)
    print(local_links[0:3])
    print("local set done")

    # создаём множество актуальных ссылок на товары прямиком с mobile.de
    with open(os.path.join(BASE_DIR, "mobile_scraper", "data", "active_links.txt"), "r") as inp:
        active_li = []
        for line in inp:
            active_li.append(line.strip())
    active_set = set(active_li)
    print("active set done")

    # вычитаем множества и получаем ссылки, которые надо пометить неактивными в таблице, а также ссылки которые
    # необходимо спарсить и дозагрузить в таблице
    del_links = local_set - active_set
    upd_links = active_set - local_set
    print('total upd links: ', len(upd_links))

    # отмечаем неактивные товары в таблице
    activity_row = []
    for link in local_links:
        if link not in del_links:
            activity_row.append(['Да'])
        else:
            activity_row.append(['Нет'])
    write_column(activity_row, 'AV2:AV')

    # очищаем товары, которые остались в json после прошлой сессии парсера
    if os.path.exists(os.path.join(BASE_DIR, 'mobile_scraper', 'data', 'products_json.txt')):
        os.remove(os.path.join(BASE_DIR, 'mobile_scraper', 'data', 'products_json.txt'))

    # непосредственно парсинг товаров и их запись в json
    print(upd_links, 'upd links')

    link_counter = 1
    proxy_id = 0
    # переменная для удаления прокси в самом конце работы программы
    last_used_proxy_id = 0

    for link in upd_links:
        # смена прокси каждые 10 запросов
        if (link_counter - 1) % 10 == 0:
            # если прокси уже было установлено, то есть это не первый запрос - удаляем его
            if link_counter != 1:
                remove_proxy(PROXY_FILENAMES[proxy_id])
            set_proxy(PROXY_FILENAMES[proxy_id])

            last_used_proxy_id = proxy_id

            # инкрементация proxy_id с учётом кол-ва прокси
            if proxy_id + 1 != len(PROXY_FILENAMES):
                proxy_id += 1
            else:
                proxy_id = 0
        try:
            print(link_counter, link, f'used proxy - {PROXY_FILENAMES[proxy_id - 1]}',)

            if os.path.exists(os.path.join(BASE_DIR, 'mobile_scraper', 'data', 'products_json.txt')):
                with open(os.path.join(BASE_DIR, 'mobile_scraper', 'data', 'products_json.txt')) as input_file:
                    data = json.load(input_file)
            else:
                data = {'products': []}

            product_data = get_data(link.strip())
            data['products'].append(product_data)

            with open(os.path.join(BASE_DIR, 'mobile_scraper', 'data', 'products_json.txt'), 'w', encoding='utf-8') \
                    as output_file:
                json.dump(data, output_file)

            link_counter += 1

        except Exception as exc:
            print(exc)

    # избавляемся от прокси в конце выполнения парсинга
    remove_proxy(last_used_proxy_id)

    # загрузка товаров из json в таблицу
    upload_data_to_sheets()
