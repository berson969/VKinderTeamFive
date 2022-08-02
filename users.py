import datetime
from dateutil.parser import parse
import requests
import os
from dotenv import load_dotenv
from pprint import pprint

from access_token import getting_tokens


def _count_likes(response):
    count_dict = {}
    for i, item in enumerate(response['response']['items']):
        count_dict[i] = sum(item['likes'].values())
    return sorted(count_dict, key=count_dict.get, reverse=True)


class VKcls:

    def __init__(self, access_token, token, version='5.131'):
        self.user_dict_info = {}
        self.photos_list = []
        self.URL = 'https://api.vk.com/method/'
        self.access_token = access_token
        self.token = token
        self.version = version
        self.params = {'access_token': self.access_token, 'v': self.version}
        self.params1 = {'access_token': self.token, 'v': self.version}

    def users_info(self, vk_id: str, length=3):
        self.length = length
        params = {'user_ids': vk_id, 'fields': 'bdate, sex, city'}
        response = requests.get(f'{self.URL}users.get', params={**self.params, **params}).json()
        print(response)
        if not response['response']:
            return False
        elif 'deactivated' in response['response'][0].keys():
            return False
        else:
            self.user_dict_info['vk_id'] = response['response'][0]['id']
            self.user_dict_info['name'] = response['response'][0]['first_name'] + ' ' + response['response'][0][
                'last_name']
            if 'city' in response['response'][0].keys():
                self.user_dict_info['city_id'] = response['response'][0]['city']['id']
                self.user_dict_info['city'] = response['response'][0]['city']['title']
            else:
                self.user_dict_info['city'] = ''
            if 'bdate' in response['response'][0].keys():
                self.user_dict_info['birth_date'] = response['response'][0]['bdate']
            else:
                self.user_dict_info['birth_year'] = ''
            self.user_dict_info['sex'] = response['response'][0]['sex']
        params1 = {'owner_id': vk_id, 'album_id': 'profile', 'extended': '1', 'photo_size': '1'}
        response1 = requests.get(f'{self.URL}photos.get', params={**self.params, **params1}).json()
        try:
            key_list = _count_likes(response1)
            # pprint(response1)
            if len(key_list) < self.length:
                self.length = len(key_list)
            for i in range(self.length):
                for result in response1['response']['items'][key_list[i]]['sizes']:
                    if result['type'] == 'x':
                        self.user_dict_info[f'photo{i}'] = result['url']
                    elif result['type'] == 'y':
                        self.user_dict_info[f'photo{i}'] = result['url']
                    elif result['type'] == 'z':
                        self.user_dict_info[f'photo{i}'] = result['url']
            return self.user_dict_info
        except KeyError:
            return self.user_dict_info

    def search_users(self, client_city, client_sex, birth_day, offset=0):
        today = datetime.datetime.now()
        bd = parse(birth_day)
        delta = (datetime.datetime.now() - parse(birth_day)).days
        age = int(delta / 365)
        # age = int((datetime.datetime.now() - parse(birth_day)).days / 365)
        if client_sex == 1:
            sex_opposite = 2
            age -= 5
        elif client_sex == 2:
            sex_opposite = 1
            age += 5
        else:
            sex_opposite = client_sex
        params = {'count': 10, 'offset': offset, 'city': client_city,
                  'sex': sex_opposite, 'status': [1, 5, 6],
                  'age from': age - 5, 'age_to': age + 5, 'has_photo': 1,
                  'fields': ['photo',' screen_name']
                  }
        response = requests.get(f'{self.URL}users.search', params={**self.params1, **params}).json()
        return response


if __name__ == '__main__':
    load_dotenv()
    access_token = os.getenv('ACCESS_TOKEN_214815089')
    # token = getting_tokens(os.getenv('VK_LOGIN'), os.getenv('VK_PASSWORD'), os.getenv('CLIENT_ID2'),
    #                       os.getenv('GROUP_ID2'))
    token = os.getenv('ACCESS_USER_berson2005@yandex.ru')
    user = VKcls(access_token, token)
    # print(user.users_info(os.getenv('N_VK_ID')))
    pprint(user.search_users( 1141821, 2, '10.10.1950'))