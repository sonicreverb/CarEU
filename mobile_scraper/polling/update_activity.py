import os.path
import datetime

from main import BASE_DIR
from mobile_scraper.GoogleSheets.gsheets import write_column
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
    for link in local_links:
        if link not in del_links:
            activity_row.append(['Да'])
        else:
            activity_row.append(['Нет'])
    write_column(activity_row, 'AX2:AX')


while True:
    try:
        update_products_activity()

        print(f"Активность товаров успешно обновлена: {datetime.datetime.now()}")
    except Exception as exc:
        print(exc, datetime.datetime.now())
