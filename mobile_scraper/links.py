import time
from selenium.webdriver.support.select import Select
from bs4 import BeautifulSoup
from mobile_scraper.scraper_main import get_htmlsoup, create_driver
from mobile_scraper.GoogleSheets.gsheets import write_column, read_column


def get_models_links():
    start_link_to_scratch = 'https://www.mobile.de/ru/'
    soup = get_htmlsoup(start_link_to_scratch)
    make_list = soup.find_all('select', {'id': 'makeModelVariant1Make'})[0]
    make_list = make_list.find_all('option')

    # XLSX_PATH = os.path.join(BASE_DIR, 'mobile_scraper', 'models_links.xlsx')
    #
    # workbook = openpyxl.load_workbook(XLSX_PATH)
    # worksheet = workbook['data']
    #
    # line_num = 2

    upload_make = []
    upload_model = []
    upload_model_id = []
    upload_links = []

    for make in make_list:
        if make.get_text() in ['───────────────', 'Не важно', 'Другие']:
            continue
        if make.get_text() == 'Abarth':
            break

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
            model_link = "https://suchen.mobile.de/fahrzeuge/search.html?dam=0&isSearchRequest=true&ms=" + car_id + ";"\
                         + models_id[value_index] + "&ref=quickSearch&sfmr=false&vc=Car"

            upload_make.append([car_make])
            upload_model.append([models_names[value_index]])
            upload_model_id.append([models_id[value_index]])
            upload_links.append([model_link])

    write_column(upload_make, 'models!A2:A')
    write_column(upload_model, 'models!B2:B')
    write_column(upload_model_id, 'models!C2:C')
    write_column(upload_links, 'models!D2:D')


def get_link_for_one_make_model():
    make_li = read_column('A', 'models')
    model_li = read_column('B', 'models')
    # model_id_li = read_column('C', 'models')
    links_li = read_column('D', 'models')

    upload_A_row = []
    upload_B_row = []
    upload_C_row = []

    for line_num in range(len(make_li)):
        soup = get_htmlsoup(links_li[line_num])

        time.sleep(5)

    #     while soup.find('span', class_='btn btn--primary btn--l next-resultitems-page'):
    #         for product_block in soup.find_all('a', class_='link--muted no--text--decoration result-item'):
    #
    #             upload_A_row.append([make_li[line_num]])
    #             upload_B_row.append([model_li[line_num]])
    #             upload_C_row.append([product_block.get('href')])
    #
    #         soup = get_htmlsoup(soup.find('span', class_='btn btn--primary btn--l next-resultitems-page')
    #                             .get('data-href'))
    #
    # write_column(upload_A_row, 'products_links!A2:A')
    # write_column(upload_B_row, 'products_links!B2:B')
    # write_column(upload_C_row, 'products_links!C2:C')


# get_models_links()
get_link_for_one_make_model()
