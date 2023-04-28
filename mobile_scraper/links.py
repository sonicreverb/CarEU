import time
from selenium.webdriver.support.select import Select
from bs4 import BeautifulSoup
from mobile_scraper.scraper_main import get_htmlsoup, create_driver


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
            driver.find_element('xpath', '/html/body/div[1]/div/section[2]/div[2]/div/div[1]/form/div[4]/div[2]/input') \
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


# def read_mark_models():
#     # чтение столбцов марок и моделей из таблицы
#     makes_li = read_column('A', 'models')
#     models_li = read_column('B', 'models')
#
#     # инициализация словаря формата - модель: [марка_модели1, марка_модели2, ...]
#     makes_models_data = {make: [] for make in set(makes_li)}
#
#     # заполнение словаря моделями
#     for indx in range(len(makes_li)):
#         makes_models_data[makes_li[indx]].append(models_li[indx])
#
#     return makes_models_data
