import json
import os.path
from _init_ import BASE_DIR
from scraper.scraper_main import create_driver, get_htmlsoup, get_data  # , write_product_to_excel
from GoogleSheets.gsheets import read_column


def get_product_links_from_page(url):
    HOST = "https://www.mobile.de"
    soup = get_htmlsoup(url, create_driver())

    # поиск и запись в массив всех ссылок на товары со страницы
    soup_a_li = soup.find_all('a', class_='vehicle-data track-event u-block js-track-event js-track-dealer-ratings')
    with open(os.path.join(BASE_DIR, "scraper", "links", "active_links.txt"), "a") as al_output:
        for link in soup_a_li:
            try:
                al_output.write(HOST + link.get('href') + "\n")
            except:
                print('error: links not found')
    print(len(soup_a_li), url)

    # переход на следующую страницу
    if soup.find('a', class_='pagination-nav pagination-nav-right btn btn--muted btn--s'):
        try:
            get_product_links_from_page(HOST + soup.find('a', class_='pagination-nav pagination-nav-right btn '
                                                                     'btn--muted btn--s').get('href'))
        except:
            print('warning: next page link not found')


def get_all_active_links():
    # очистка содержимого active_links.txt
    with open(os.path.join(BASE_DIR, "scraper", "links", "active_links.txt"), "w"):
        pass

    with open(os.path.join(BASE_DIR, "scraper", "links", "filtered_links.txt")) as fl_input:
        for filtered_link in fl_input:
            get_product_links_from_page(filtered_link)


def get_local_links():
    return read_column('D')


XLSX_PATH = os.path.join(BASE_DIR, 'scraper', 'excel tables', 'product_data.xlsx')
CSV_PATH = os.path.join(BASE_DIR, 'scraper', 'excel tables', 'product_data.csv')


def update_links():
    local_links = get_local_links()
    local_set = set(link for link in local_links)
    print("local set done")

    get_all_active_links()
    with open(os.path.join(BASE_DIR, "scraper", "links", "active_links.txt"), "r") as inp:
        active_li = []
        for line in inp:
            active_li.append(line.strip())
    active_set = set(active_li)
    print("active set done")

    del_links = local_set - active_set
    upd_links = active_set - local_set

    tmp = 1
    for link in upd_links:
        try:
            print(tmp, link)

            if os.path.exists('products_json.txt'):
                with open('products_json.txt') as input_file:
                    data = json.load(input_file)
            else:
                data = {}
                data['products'] = []

            product_data = get_data(link.strip(), create_driver())
            data['products'].append(product_data)

            with open('products_json.txt', 'w') as output_file:
                json.dump(data, output_file)

            tmp += 1

        except:
            pass


    # отметка неактивных в таблице
    # workbook = load_workbook(XLSX_PATH)
    # worksheet = workbook['data']
    #
    # del_line_nums = []
    #
    # for link in del_links:
    #   print("del", link)
    #    #del_line_nums.append(int(local_dict[link]))
    #    line_num = str(local_dict[link])
    #    worksheet["BA" + line_num] = "Нет"
    #
    # workbook.save(XLSX_PATH)
    # workbook.close()

    # upload_csv_to_sheets(XLSX_PATH, CSV_PATH)

    # удаление неактивных строк из таблицы
    # workbook = load_workbook(XLSX_PATH)
    # worksheet = workbook['data']
    #
    # del_line_nums.sort()
    # for del_num in reversed(del_line_nums):
    #   worksheet.delete_rows(del_num)
    #    print(del_num)
    #
    # workbook.save(XLSX_PATH)
    # workbook.close()

    # добавление в таблицу новых товаров
    # print(len(upd_links))
    # tmp = 1
    # for link in upd_links:
    #    try:
    #        print("upd", tmp, link)
    #        data = get_data(link.strip(), create_driver())
    #        write_product_to_excel(data)
    #        if tmp % 100 == 0:
    #            upload_csv_to_sheets(XLSX_PATH, CSV_PATH)
    #        tmp += 1
    #    except:
    #        pass

    # запись и чтение в json


update_links()

