from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from main import BASE_DIR
import json
import pickle
import os.path
import time


def create_driver():
    chrome_options = webdriver.ChromeOptions()
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    return driver


def auth_and_get_cookies():
    # данные для авторизации
    with open(os.path.join(BASE_DIR, 'mobile_scraper', 'authentication', 'mobile_credentials.json'), encoding='utf-8') as f:
        creds = json.load(f)

    EMAIL = creds['email']
    PASSWORD = creds['password']
    auth_url = "https://id.mobile.de/login?service=https%3A%2F%2Fid.mobile.de%2Foauth2.0%2FcallbackAuthorize%3Fclient_id%3Dmobile_web_DL1WJUPw%26redirect_uri%3Dhttps%253A%252F%252Fwww.mobile.de%252Fapi%252Fauth%252FloginCallback%253F%26response_type%3Dcode%26response_mode%3Dquery%26client_name%3DCasOAuthClient&lang=de&state=eyJybmQiOiIyYk9vYjZ1MS1pUERrYXJyQUxZcXFMSUx5X2l5YkRDOU1hYy1sbkgyREtrIiwic3JjIjoiaHR0cHM6Ly93d3cubW9iaWxlLmRlLyJ9&nonce=HK1W5WrtzGxUJWN_N5AKTHOBdd0xdrps8VaLzR9cqGE&scope=openid"

    driver = create_driver()
    driver.get(auth_url)

    # автоматизированная авторизация 2 раза вследствии проверок на бот
    for tmp in range(2):
        time.sleep(5)

        email_input = driver.find_element(By.ID, "login-username")
        email_input.clear()
        email_input.send_keys(EMAIL)

        password_input = driver.find_element(By.ID, "login-password")
        password_input.clear()
        password_input.send_keys(PASSWORD)

        # кнопки принятия пользовательского соглашения, подтвердить логин
        time.sleep(5)
        if tmp == 0:
            accept_privacy_button = driver.find_element(By.XPATH, "/html/body/div[3]/div[2]/div[2]/div[1]/button")
            accept_privacy_button.click()
        submit_button = driver.find_element(By.ID, "login-submit")
        submit_button.click()

        time.sleep(30)
    login_button = driver.find_element(By.XPATH, "/html/body/div[1]/header/div[1]/div[2]/div/div[2]/div/button")
    login_button.click()

    time.sleep(10)

    # кукис
    pickle.dump(driver.get_cookies(), open(os.path.join(BASE_DIR, 'mobile_scraper', 'authentication', 'cookies.pkl'), 'wb'))


def test_with_cookies():
    driver = create_driver()
    driver.get("https://www.mobile.de/")

    time.sleep(5)

    for cookie in pickle.load(open(os.path.join(BASE_DIR, 'mobile_scraper', 'authentication', 'cookies.pkl'), 'rb')):
        driver.add_cookie(cookie)

    time.sleep(5)
    driver.refresh()
    time.sleep(10)
