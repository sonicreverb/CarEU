import datetime
import re

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from googletrans import Translator
from mobile_scraper.telegram_alerts.telegram_notifier import send_notification


# возвращает driver
def create_driver():
    print('[DRIVER INFO] Driver created successfully.\n')
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()))


# закрывает все окна и завершает сеанс driver
def kill_driver(driver):
    driver.close()
    driver.quit()
    print('[DRIVER INFO] Driver was closed successfully.\n')


# возвращает soup указанной страницы
def get_htmlsoup(driver):
    try:
        # обработка случая, при котором доступ к сайту заблокирован
        if "Zugriff verweigert / Access denied" in driver.page_source:
            notification = "Error! Access to mobile denied."
            send_notification(f"[CAREU] Во время сессии возникла ошибка ({str(datetime.datetime.now())[:-7]}).\n"
                              f"Информация об ошибке: {notification}")
            raise SystemExit(f"[GET HTML] {notification}")

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        return soup

    except Exception as exc:
        print(exc)
        return None


# возвращает словарь product_data с данными о товаре указанной страницы
def get_data(soup, url=None):
    try:
        if not soup:
            return None

        title = soup.find('h1', class_='h2 g-col-8').get_text()

        # находим цены, которые расположены в одном блоке
        price_match = soup.find('div', class_='header-price-box g-col-4')
        if price_match:
            if "Нетто" in price_match.get_text() and "Брутто" in price_match.get_text():
                rawtext = ''.join(price_match.get_text().split())
                prices = re.findall(r'\d+', rawtext)

                brutto_price = int(prices[0])
                netto_price = int(prices[1])
            else:
                print("[GET DATA INFO] No netto or brutto prices.")
                return None
        else:
            print("[GET DATA INFO] No netto or brutto prices.")
            return None

        soup_img_li = soup.find_all('div', class_='gallery-bg js-gallery-img js-load-on-demand')
        img_li = []
        for img_index in range(len(soup_img_li) // 2 - 1):
            img_li.append(soup_img_li[img_index].get('data-src'))

        if len(img_li) < 8:
            print("[GET DATA INFO] Not enough images.")
            return None

        technical_options_soup_li = soup.find('div', class_='vip-details-block u-margin-bottom-18') \
            .find_all('span', {'class': 'g-col-6'})
        techopt_dict = {}
        # меня напрягает и фрустрирует, что линтер ругается на это, поэтому ЭТО здесь
        col_key = 'error'

        for col_index in range(len(technical_options_soup_li)):
            if col_index % 2 == 0:
                col_key = technical_options_soup_li[col_index].get_text()
            else:
                col_value = technical_options_soup_li[col_index].get_text().replace(u'\u2009', u' ')
                techopt_dict[col_key] = col_value.replace(u'\xa0', u' ')

        # фильтр по дате (не больше, чем 5 давности лет для машины)
        if int(datetime.datetime.now().strftime("%y")) - int(techopt_dict['Первая регистрация'][-2:]) == 5:
            if int(datetime.datetime.now().strftime("%m")) > int(techopt_dict['Первая регистрация'][:2]):
                print("[GET DATA INFO] Too old release date.")
                return None

        characteristics = ''
        for row in soup.find_all('p', class_='bullet-point-text'):
            characteristics += row.get_text() + '; '

        description_soup = soup.find('div', class_='description-text js-original-description g-col-12')
        description_headlines = description_soup.find_all('b')
        description_ul = description_soup.find_all('ul')
        description_str = ''

        if len(description_ul) == 0:
            description_str = soup.find('div', class_='description-text js-original-description g-col-12').get_text()
        else:
            for index in range(len(description_headlines)):
                if index >= len(description_ul):
                    break
                description_str += description_headlines[index].get_text() + '\n'
                for li in description_ul[index].find_all('li'):
                    description_str += li.get_text() + '\n'
                description_str += '\n'

        description_translated = Translator().translate(text=description_str.strip(), src='de', dest='ru').text

        dealer_name = soup.find('div', class_='vip-box seller-box cBox cBox--content hidden-s u-clearfix'). \
            find('a', {'data-google-interstitial': 'false'}).get_text()

        dealer_phone = ''.join(soup.find('p', class_='seller-phone u-margin-bottom-9 u-text-orange u-text-bold')
                               .get_text().split())
        dealer_link = soup.find('div', class_='vip-box seller-box cBox cBox--content hidden-s u-clearfix') \
            .find('a').get('href')

        product_data = {'Title': title, 'URL': url, 'BruttoPrice': brutto_price, 'NettoPrice': netto_price,
                        'ImgLi': img_li, 'TechOptDict': techopt_dict, 'CharacteristicsStr': characteristics,
                        'DescriptionStr': description_str.strip(), 'DescriptionTRD': description_translated,
                        'DealerData': [dealer_name, dealer_link, dealer_phone]}

        return product_data
    except Exception as ex:
        print(f"{ex} in line 99 scraper_main.py")
        return None
