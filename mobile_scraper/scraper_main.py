from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup


def create_driver():
    chrome_options = webdriver.ChromeOptions()
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    return driver


def get_htmlsoup(url):
    driver = create_driver()

    # проверка на валидность куки
    # try:
    #     cookies_birthday = os.path.getmtime(os.path.join(BASE_DIR, 'mobile_scraper', 'authentication', 'cookies.pkl'))
    #     if time.ctime(cookies_birthday).split()[2] != str(datetime.now().day):
    #         auth_and_get_cookies()
    # except FileNotFoundError:
    #     auth_and_get_cookies()

    try:
        # загружаем куки
        driver.get(url)
        #
        # time.sleep(20)
        #
        # for cookie in pickle.load(open(os.path.join(BASE_DIR, 'mobile_scraper', 'authentication', 'cookies.pkl'),
        #                                'rb')):
        #     driver.add_cookie(cookie)
        #
        # driver.refresh()

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        driver.close()
        return soup

    except Exception as exc:
        print(exc, url)
        return 'error invalid url'


def get_data(url):
    soup = get_htmlsoup(url)
    if soup == 'error invalid url':
        return None

    title = soup.find('h1', class_='h2 g-col-8').get_text()
    brutto_price = ''.join(soup.find('span', class_='brutto-price u-text-bold').get_text()[:-10].split())
    netto_price = ''.join(soup.find('p', class_='netto-price').get_text()[:-9].split())

    soup_img_li = soup.find_all('div', class_='gallery-bg js-gallery-img js-load-on-demand')
    img_li = []
    for img_index in range(len(soup_img_li) // 2 - 1):
        img_li.append(soup_img_li[img_index].get('data-src'))

    technical_options_soup_li = soup.find('div', class_='vip-details-block u-margin-bottom-18') \
        .find_all('span', {'class': 'g-col-6'})
    TO_dict = {}
    # меня напрягает и фрустрирует, что линтер ругается на это, поэтому ЭТО здесь
    col_key = 'error'

    for col_index in range(len(technical_options_soup_li)):
        if col_index % 2 == 0:
            col_key = technical_options_soup_li[col_index].get_text()
        else:
            col_value = technical_options_soup_li[col_index].get_text().replace(u'\u2009', u' ')
            TO_dict[col_key] = col_value.replace(u'\xa0', u' ')

    characteristics = ''
    for row in soup.find_all('p', class_='bullet-point-text'):
        characteristics += row.get_text() + '; '

    # todo !
    description_soup = soup.find('div', class_='description-text js-original-description g-col-12')
    description_headlines = description_soup.find_all('b')
    description_ul = description_soup.find_all('ul')
    description_str = ''

    if len(description_ul) == 0:
        description_str = soup.find('div', class_='description-text js-original-description g-col-12').get_text()
    else:
        for index in range(len(description_headlines)):
            # todo !!
            if index >= len(description_ul):
                break
            description_str += description_headlines[index].get_text() + '\n'
            for li in description_ul[index].find_all('li'):
                description_str += li.get_text() + '\n'
            description_str += '\n'

    dealer_name = soup.find('div', class_='vip-box seller-box cBox cBox--content hidden-s u-clearfix'). \
        find('a', {'data-google-interstitial': 'false'}).get_text()

    dealer_phone = ''.join(soup.find('p', class_='seller-phone u-margin-bottom-9 u-text-orange u-text-bold').get_text()
                           .split())
    dealer_link = soup.find('div', class_='vip-box seller-box cBox cBox--content hidden-s u-clearfix') \
        .find('a').get('href')

    product_data = {'Title': title, 'URL': url, 'BruttoPrice': brutto_price, 'NettoPrice': netto_price, 'ImgLi': img_li,
                    'TechOptDict': TO_dict, 'CharacteristicsStr': characteristics,
                    'DescriptionStr': description_str.strip(), 'DealerData': [dealer_name, dealer_link, dealer_phone]}

    return product_data
