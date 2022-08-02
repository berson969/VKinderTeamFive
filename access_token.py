import time

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import re
import os

load_dotenv('.env', override=True)


# PATTERN_GROUP = r"(https://oauth.vk.com/blank.html#expires_in=0&)(access_token)(\_)(\d+)(\=)([a-zA-Z0-9\.\-\_]+)"
# PATTERN_USER = r"(https://oauth.vk.com/blank.html#)(access_token=)([a-f0-9]+)"


class AuthAccess:
    def __init__(self, login, password, client_id, group_id):
        self.login = login
        self.password = password
        self.client_id = client_id
        self.group_id = group_id
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    # Автоматическое получение Authorization Code Flow для получения ключа доступа сообщества
    def get_token(self, url, pattern, token_name) -> str:
        # self.url = url
        # self.pattern = pattern
        # self.token_name = token_name
        if os.getenv(token_name) is not None:
            return os.getenv(token_name)
        self.driver.get(url)
        WebDriverWait(self.driver, 30).until \
            (EC.presence_of_element_located((By.XPATH, "//button[@class='flat_button oauth_button button_wide']")))
        login_form = self.driver.find_element(By.NAME, 'email')
        login_form.send_keys(self.login)
        password_form = self.driver.find_element(By.NAME, 'pass')
        password_form.send_keys(self.password)
        button_form = self.driver.find_element(By.XPATH, "//button[@class='flat_button oauth_button button_wide']")
        button_form.click()
        WebDriverWait(self.driver, 30).until(EC.presence_of_element_located
                                        ((By.XPATH, "//*[@class='flat_button fl_r button_indent']")))
        time.sleep(1)
        button_form = self.driver.find_element(By.XPATH, "//button[@class='flat_button fl_r button_indent']")
        button_form.click()
        time.sleep(1)
        token = re.sub(pattern, r'\4', self.driver.current_url)
        next_ = open('.env', 'a')
        next_.writelines(f"{token_name} = '{token}'\n")
        next_.close()
        return token


def getting_tokens(login, password, client_id, group_id):
    user_token = AuthAccess(login, password, client_id, group_id)
    url_group = f'https://oauth.vk.com/authorize?client_id={client_id}&group_ids={group_id}' \
                f'&redirect_uri=https://vk.com/club214815089&display=page&scope=messages&response_type=token&v=5.131'
    PATTERN_GROUP = r"(https://api.vk.com/blank.html#expires_in=0&access_token_)(\d+)(\=)([a-zA-Z0-9\.\-\_]+)"
    token_name_group = f'ACCESS_TOKEN_{group_id}'
    token = user_token.get_token(url_group, PATTERN_GROUP, token_name_group)

    PATTERN_USER = r"(https://api.vk.com/blank.html)(\#)(access_token=)([a-zA-Z0-9\.\_\-]+)(\.+)"
    url_user = f'https://oauth.vk.com/authorize?client_id={client_id}&redirect_uri=' \
               f'https://vk.com/club214815089&display=page&scope=friends,groups&response_type=token&v=5.131&state=347650&revoke=1'
    token_user = f'ACCESS_USER_{login}'
    access_token = user_token.get_token(url_user, PATTERN_USER, token_user)
    return token, access_token


if __name__ == '__main__':
    group_id = '214792702'
    group_id2 = '214815089'
    client_id2 = '8231976'
    login = 'berson2005@yandex.ru'
    password = 'Bb19690226'
    token, access_token = getting_tokens(login, password, client_id2, group_id2)
    print(access_token)
    print(token)

# URL = 'https://oauth.vk.com/authorize'
# params = {'client_id': client_id2, 'redirect_uri': 'https://vk.com/id204323306', 'group_ids': group_id2, 'display': 'page', 'scope': 'messages', 'response_type': 'token', 'v': '5.131', 'state': '12345'}
# response = requests.get(URL, params=params)
# print(response.text)

# URL2 = 'https://oauth.vk.com/access_token'
# params = {'client_id': client_id2, 'client_secret': client_secret2, 'grant_type': 'client_credentials', 'v': '5.131'}
# response1 = requests.get(URL2, params=params)
# print(response1.text)


# client_secret2 = ''
# code = ''
# params = {'client_id': client_id2, 'client_secret': client_secret2, 'redirect_uri': 'https://oauth.vk.com/blank.html', 'code': code}
# response2 = requests.post(URL2, params=params)
# print(response2.text)
