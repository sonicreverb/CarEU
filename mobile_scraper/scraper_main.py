import re
import os
import undetected_chromedriver
# import zipfile

# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from googletrans import Translator
# from mobile_scraper.telegram_alerts.telegram_notifier import send_notification
from datetime import datetime

BASE_DIR = "C:\\Users\\careu\\PycharmProjects\\CarEU"

# кол-во доступных прокси конфигов
AVAILABLE_PROXIES_NUM = 3
current_proxy_num = 0

# глобальная переменная для
driver_requests = 0


# считывает из файла proxy.txt параметры прокси
def get_proxy_creds(filename="proxy.txt"):
    if not filename:
        return None

    result = {'host': '', 'port': '', 'login': '', 'password': ''}
    proxy_path = os.path.join(BASE_DIR, 'mobile_scraper', filename)
    if os.path.exists(proxy_path):
        with open(proxy_path, 'r') as file:
            array_of_lines = file.readlines()
        result['host'] = array_of_lines[0].strip()
        result['port'] = array_of_lines[1].strip()
        result['login'] = array_of_lines[2].strip()
        result['password'] = array_of_lines[3].strip()

        print(f'[SET PROXY] Данные прокси из \'{filename}\' успешно получены '
              f'({result["host"]}:{result["port"]} login - {result["login"]} password - {result["password"]})')
        return result
    else:
        print(f'[SET PROXY] Не удалось найти файл с настройками прокси \'{filename}\'')
        return None


manifest_json = """
{
    "version": "1.0.0",
    "manifest_version": 2,
    "name": "Chrome Proxy",
    "permissions": [
        "proxy",
        "tabs",
        "unlimitedStorage",
        "storage",
        "<all_urls>",
        "webRequest",
        "webRequestBlocking"
    ],
    "background": {
        "scripts": ["background.js"]
    },
    "minimum_chrome_version":"22.0.0"
}
"""


# # возвращает driver
# def create_driver(proxy_filename=None):
#     chrome_options = Options()
#
#     try:
#         proxy_data = get_proxy_creds(proxy_filename)
#     except Exception as _ex:
#         print(f'[SET PROXY] Не удалось получить параметры прокси. Ошибка ({_ex})')
#         proxy_data = False
#
#     if proxy_data:
#         proxy_host = proxy_data.get('host')
#         proxy_port = proxy_data.get('port')
#         proxy_username = proxy_data.get('login')
#         proxy_password = proxy_data.get('password')
#
#         background_js = """
#                    var config = {
#                            mode: "fixed_servers",
#                            rules: {
#                            singleProxy: {
#                                scheme: "http",
#                                host: "%s",
#                                port: parseInt(%s)
#                            },
#                            bypassList: ["localhost"]
#                            }
#                        };
#
#                    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});
#
#                    function callbackFn(details) {
#                        return {
#                            authCredentials: {
#                                username: "%s",
#                                password: "%s"
#                            }
#                        };
#                    }
#
#                    chrome.webRequest.onAuthRequired.addListener(
#                                callbackFn,
#                                {urls: ["<all_urls>"]},
#                                ['blocking']
#                    );
#                    """ % (proxy_host, proxy_port, proxy_username, proxy_password)
#         pluginfile = os.path.join(BASE_DIR, 'proxy_auth_plugin.zip')
#         with zipfile.ZipFile(pluginfile, 'w') as zp:
#             zp.writestr("manifest.json", manifest_json)
#             zp.writestr("background.js", background_js)
#         chrome_options.add_extension(pluginfile)
#
#     # prefs = {"profile.managed_default_content_settings.images": 2}
#     # chrome_options.add_experimental_option("prefs", prefs)
#     chrome_options.add_argument("user-agent=Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 "
#                                 "Firefox/84.0")
#     chrome_options.add_argument("--disable-blink-features=AutomationControlled")
#
#     driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
#
#     # print('[DRIVER INFO] Driver created successfully with images disabled.\n')
#     return driver
#     # print('[DRIVER INFO] Driver created successfully.\n')
#     # return webdriver.Chrome(service=Service(ChromeDriverManager().install()))
#
#
# # закрывает все окна и завершает сеанс driver
# def kill_driver(driver):
#     driver.close()
#     driver.quit()
#     print('[DRIVER INFO] Driver was closed successfully.\n')


# UNDETECTED DRIVER VER
def create_driver(proxy_filename="proxy.txt"):
    proxy_data = get_proxy_creds(proxy_filename)
    host = proxy_data.get('host', '')
    port = proxy_data.get('port', '')
    login = proxy_data.get('login', '')
    password = proxy_data.get('password', '')

    options = undetected_chromedriver.ChromeOptions()
    options.add_argument(f'--proxy-server=http://{login}:{password}@{host}:{port}')
    return undetected_chromedriver.Chrome(options=options)


def kill_driver(driver):
    try:
        driver.quit()
    except Exception:
        pass


def reload_driver_proxy(driver):
    global current_proxy_num
    # перезагрузка драйвера каждые 50 запросов и смена прокси
    # if driver_requests % 10 == 0:
    old_url = driver.current_url
    kill_driver(driver)

    current_proxy_num = (current_proxy_num + 1) % AVAILABLE_PROXIES_NUM
    driver = create_driver(f"proxy_{current_proxy_num}.txt")
    driver.get(old_url)
    print(f'[GET HTMLSOUP] Переключение прокси на \'proxy_{current_proxy_num}.txt\' успешно!')

    return driver


# возвращает soup указанной страницы
def get_htmlsoup(driver):
    try:
        # обработка случая, при котором доступ к сайту заблокирован
        if "Zugriff verweigert / Access denied" in driver.page_source:
            notification = "Error! Access to mobile denied."
            # send_notification(f"[CAREU] Во время сессии возникла ошибка ({str(datetime.now())[:-7]}).\n"
            #                   f"Информация об ошибке: {notification}")
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
        date_string = techopt_dict['Первая регистрация']
        input_date = datetime.strptime(date_string, "%m/%Y")
        current_date = datetime.now()
        first_day_of_current_month = datetime(current_date.year, current_date.month, 1)
        age_diff = (first_day_of_current_month - input_date).days / 365

        if age_diff >= 5 or age_diff <= 2.8:
            print("[GET DATA INFO] Incorrect release date.")
            print(date_string, age_diff)
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
