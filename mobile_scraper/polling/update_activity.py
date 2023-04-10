import os.path
import datetime

from main import BASE_DIR
from mobile_scraper.GoogleSheets.gsheets import write_column, read_column, delete_row
from mobile_scraper.updater import get_local_links, HOST
from mobile_scraper.scraper_main import get_htmlsoup


# по сути переопределение функции из updater для другого текстового файла во избежание конфликтов
def get_product_links_from_page(url):
    soup = get_htmlsoup(url)

    # поиск и запись в массив всех ссылок на товары со страницы
    soup_a_li = soup.find_all('a', class_='vehicle-data track-event u-block js-track-event js-track-dealer-ratings')
    with open(os.path.join(BASE_DIR, "mobile_scraper", "data", "activity_links.txt"), "a") as al_output:
        for link in soup_a_li:
            try:
                al_output.write(HOST + link.get('href') + "\n")
            except Exception as excep:
                print('error: links not found', excep)
    print(len(soup_a_li), url)

    # переход на следующую страницу
    if soup.find('a', class_='pagination-nav pagination-nav-right btn btn--muted btn--s'):
        try:
            get_product_links_from_page(HOST + soup.find('a', class_='pagination-nav pagination-nav-right btn '
                                                                     'btn--muted btn--s').get('href'))
        except Exception as excep:
            print('warning: next page link not found', excep)


def get_all_active_links():
    # очистка содержимого active_links.txt
    with open(os.path.join(BASE_DIR, "mobile_scraper", "data", "activity_links.txt"), "w"):
        pass

    with open(os.path.join(BASE_DIR, "mobile_scraper", "data", "filtered_links.txt")) as fl_input:

        for filtered_link in fl_input:
            get_product_links_from_page(filtered_link)


def update_products_activity():
    get_all_active_links()

    # создаём множество ссылок на товары из таблицы
    local_links = get_local_links()
    local_set = set(link for link in local_links)

    # создаём множество актуальных ссылок на товары прямиком с mobile.de
    with open(os.path.join(BASE_DIR, "mobile_scraper", "data", "activity_links.txt"), "r") as inp:
        active_li = []
        for line in inp:
            active_li.append(line.strip())
    active_set = set(active_li)

    # вычитаем множества и получаем ссылки, которые надо пометить неактивными в таблице +
    # необходимо спарсить и дозагрузить в таблице
    del_links = local_set - active_set

    # отмечаем неактивные товары в таблице
    activity_row = []

    # модуль удаления неактивных товаров, которым уже больше суток
    unactive_since_column = read_column('AY', 'data')

    row_id = 2
    for date_str in unactive_since_column:
        if date_str != "-":
            date_in_table = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
            date_current = datetime.datetime.now()

            delta = date_current - date_in_table
            print(f'Строка {row_id}. Разница между датами: {delta}')

            if delta.days > 1:
                print(f'Индекс строки для удаления - {row_id}')
                delete_row(row_id, 'data')
        row_id += 1

    # как только товар станет неактивным, нам нужно записать время в таблицу, чтобы через сутки удалить строку с товаром
    unactive_since_row = []
    unactive_since_column = read_column('AY', 'data')
    unactive_since_arr_id = 0

    for link in local_links:
        if link not in del_links:
            unactive_since_row.append(['-'])
            activity_row.append(['Да'])
        else:
            activity_row.append(['Нет'])
            if unactive_since_column[unactive_since_arr_id] == '-':
                unactive_since_row.append([datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
            else:
                unactive_since_row.append([unactive_since_column[unactive_since_arr_id]])
        unactive_since_arr_id += 1

    write_column(activity_row, 'AX2:AX')
    write_column(unactive_since_row, 'AY2:AY')


while True:
    try:
        update_products_activity()

        print(f"Активность товаров успешно обновлена: {datetime.datetime.now()}")
    except Exception as exc:
        print(exc, datetime.datetime.now())
