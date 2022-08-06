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
LOGIN = os.getenv('VK_LOGIN')
PASSWORD = os.getenv('VK_PASSWORD')


class AuthAccess:
    def __init__(self, client_id, group_id=0):
        self.client_id = client_id
        self.group_id = group_id
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    # Authorization Code Flow method for get tokens by selenium
    def get_token(self, url, pattern, token_name) -> str:
        if os.getenv(token_name) is not None:
            return os.getenv(token_name)
        self.driver.get(url)
        WebDriverWait(self.driver, 30).until \
            (EC.presence_of_element_located((By.XPATH, "//button[@class='flat_button oauth_button button_wide']")))
        login_form = self.driver.find_element(By.NAME, 'email')
        login_form.send_keys(LOGIN)
        password_form = self.driver.find_element(By.NAME, 'pass')
        password_form.send_keys(PASSWORD)
        button_form = self.driver.find_element(By.XPATH, "//button[@class='flat_button oauth_button button_wide']")
        button_form.click()
        WebDriverWait(self.driver, 30).until(EC.presence_of_element_located
                                             ((By.XPATH, "//*[@class='flat_button fl_r button_indent']")))
        time.sleep(1)
        button_form = self.driver.find_element(By.XPATH, "//button[@class='flat_button fl_r button_indent']")
        button_form.click()
        token = re.sub(pattern, r'\4', self.driver.current_url)
        next_ = open('.env', 'a')
        next_.writelines(f"{token_name} = '{token}'\n")
        next_.close()
        return token


# Getting token by Implicit Flow for groups  https://dev.vk.com/api/access-token/implicit-flow-community
def group_token_get(client_id, group_id):
    PATTERN_GROUP = r"(https://api.vk.com/blank.html#expires_in=0&access_token_)(\d+)(\=)([a-zA-Z0-9\.\-\_]+)"
    group_creator = AuthAccess(client_id, group_id)
    url_group = f'https://oauth.vk.com/authorize?client_id={client_id}&group_ids={group_id}' \
                f'&redirect_uri=https://vk.com/club214815089&display=page' \
                f'&scope=messages,photos,stories,manage,docs&response_type=token&v=5.131'
    group_token_name = f'GROUP_TOKEN_{group_id}'
    return group_creator.get_token(url_group, PATTERN_GROUP, group_token_name)


# Getting token by Authorization Code Flow for users https://dev.vk.com/api/access-token/authcode-flow-user
def user_token_get(client_id):
    PATTERN_USER = r"(https://api.vk.com/blank.html)(\#)(access_token=)([a-zA-Z0-9\.\_\-]+)" \
                   r"(\&)(expires_in=)(\d+)(\&)(user_id=)(\d+)(\&)(state=347650)"
    user_creator = AuthAccess(client_id)
    url_user = f'https://oauth.vk.com/authorize?client_id={client_id}&redirect_uri=' \
               f'https://vk.com/club214815089&display=page&scope=friends,groups' \
               f'&response_type=token&v=5.131&state=347650&revoke=1'
    user_token = f'USER_TOKEN_{LOGIN}'
    return user_creator.get_token(url_user, PATTERN_USER, user_token)


if __name__ == '__main__':
    group_id = '214792702'
    group_id2 = '214815089'
    client_id2 = '8231976'
    access_token = group_token_get(client_id2, group_id2)
    print(access_token)
    access_user = user_token_get(client_id2)
    print(access_user)
