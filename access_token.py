import os
import re
import time

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

load_dotenv('.env', override=True)
LOGIN = os.getenv('VK_LOGIN')
PASSWORD = os.getenv('VK_PASSWORD')
PATTERN_GROUP = r"(https://api.vk.com/blank.html#expires_in=0&access_token_)" \
                r"(\d+)(\=)([a-zA-Z0-9\.\-\_]+)"
PATTERN_USER = r"(https://api.vk.com/blank.html)(\#)(access_token=)([a-zA-Z0-9\.\_\-]+)" \
                   r"(\&)(expires_in=)(\d+)(\&)(user_id=)(\d+)(\&)(state=347650)"


def get_token(url: str, pattern: str, token_name: str) -> str:
    """
            Authorization Code Flow method for get tokens by selenium
            writing  different tokens  to file .env
            IMPORTANT!! Need switch to push authorization in VK app
            https://grandguide.ru/otklyuchit-dvuhfaktornuyu-autentifikaciyu-vk-vkontakte/

    :param url:
    :param pattern:
    :param token_name: str
    :return: token: str

    """
    if os.getenv(token_name) is not None:

        flag = input('The token already exists. Renew it? Y/n ').lower()
        if flag == 'y':
            file_new = ''
            with open('.env', 'r', encoding='UTF-8') as reading:
                for line in reading.readlines():
                    if line.find(token_name) == -1:
                        file_new += line
            with open('.env', 'w', encoding='UTF-8') as writing:
                writing.write(file_new)
        else:
            return os.getenv(token_name)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(url)
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//button[@class='flat_button "
                                                                                   "oauth_button button_wide']")))
    login_form = driver.find_element(By.NAME, 'email')
    login_form.send_keys(LOGIN)
    password_form = driver.find_element(By.NAME, 'pass')
    password_form.send_keys(PASSWORD)
    button_form = driver.find_element(By.XPATH, "//button[@class='flat_button oauth_button button_wide']")
    button_form.click()
    WebDriverWait(driver, 30).until(EC.presence_of_element_located
                                         ((By.XPATH, "//*[@class='flat_button fl_r button_indent']")))
    time.sleep(1)
    button_form = driver.find_element(By.XPATH, "//button[@class='flat_button fl_r button_indent']")
    button_form.click()
    token = re.sub(pattern, r'\4', driver.current_url)
    with open('.env', 'a', encoding='UTF-8') as file:
        file.writelines(f"{token_name} = '{token}'\n")
    return token


def group_token_get(client_id, group_id):
    """
            Getting token by Implicit Flow for groups
              https://dev.vk.com/api/access-token/implicit-flow-communityn
    :param client_id: int
    :param group_id: int

    :return: GROUP_TOKEN: str
    """
    url_group = f'https://oauth.vk.com/authorize?client_id={client_id}&group_ids={group_id}' \
                f'&redirect_uri=https://vk.com/club214815089&display=page' \
                f'&scope=messages,photos,stories,manage,docs&response_type=token&v=5.131'
    return get_token(url_group, PATTERN_GROUP, 'GROUP_TOKEN')


def user_token_get(client_id):
    """
            Getting token by Authorization Code Flow for users
             https://dev.vk.com/api/access-token/authcode-flow-user
    :param client_id: int

    :return: USER_TOKEN: str
    """
    url_user = f'https://oauth.vk.com/authorize?client_id={client_id}&redirect_uri=' \
               f'https://vk.com/club214815089&display=page&scope=friends,groups' \
               f'&response_type=token&v=5.131&state=347650&revoke=1'
    return get_token(url_user, PATTERN_USER, 'USER_TOKEN')


if __name__ == '__main__':
    access_token = group_token_get(os.getenv('CLIENT_ID2'), os.getenv('GROUP_ID'))
    print(access_token)
    access_user = user_token_get(os.getenv('CLIENT_ID2'))
    print(access_user)
