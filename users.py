import requests
import os
from dotenv import load_dotenv
from pprint import pprint


class VK:

    def __init__(self, access_token, version='5.131'):
        self.user_dict_info = {}
        self.photos_list = []
        self.URL = 'https://api.vk.com/method/'
        self.token = access_token
        self.version = version
        self.params = {'access_token': self.token, 'v': self.version}

    def users_info(self, vk_id: str):
        params = {'user_ids': vk_id, 'fields': 'bdate, sex, city'}
        response = requests.get(f'{self.URL}users.get', params={**self.params, **params}).json()
        if not response['response']:
            return False
        elif 'deactivated' in response['response'][0].keys():
            return False
        else:
            self.user_dict_info['vk_id'] = response['response'][0]['id']
            self.user_dict_info['name'] = response['response'][0]['first_name'] + ' ' + response['response'][0][
                'last_name']
            if 'city' in response['response'][0].keys():
                self.user_dict_info['city'] = response['response'][0]['city']['title']
            else:
                self.user_dict_info['city'] = None #если город не указан поиск будет тоже без указания на конкретный город
            if 'bdate' in response['response'][0].keys():
                if len(response['response'][0]['bdate'].split('.')) == 3:
                    self.user_dict_info['birth_year'] = int(response['response'][0]['bdate'].split('.')[-1])
                else:
                    self.user_dict_info['birth_year'] = None #если год рождения не указан поиск будет тоже без указания на конкретный год рождения
            else:
                self.user_dict_info['birth_year'] = None  #если дата рождения не указан поиск будет тоже без указания на конкретной даты рождения
            self.user_dict_info['sex'] = response['response'][0]['sex']
        try:
            return self.user_dict_info
        except KeyError:
            return self.user_dict_info

    def search_users(self, birth_year, sex: int, sity: str):
        '''
        функция  выводит список пользователей в виде словаря с ключами: 'id' и 'имя'
        '''
        user_list = []
        #sex = [2, 1][sex-1] эта строка меняет пол на противоположный, надо вставить перед вызовом этой функии
        # и еще может быть значение 0 когда пол не указан, тоже надо учесть
        params = {'hometown': sity, 'birth_year': birth_year, 'sex': sex}
        response = requests.get(f'{self.URL}users.search', params={**self.params, **params}).json()
        for el in response['response']['items']:
            user_info_dict = {'id': el['id'], 'name': el['first_name'] + ' ' + el['last_name']}
            user_list.append(user_info_dict)
        return user_list

    def photos_get(self, vk_id: str):
        '''функция выводит список словарей состоящих из ID фотографии
        и количества лайков 3 самых популярных фотографий
        '''
        photo_list = []
        params = {'owner_id': vk_id, 'album_id': 'profile', 'extended': '1', 'photo_size': '1'}
        response = requests.get(f'{self.URL}photos.get', params={**self.params, **params}).json()
        for item in response['response']['items']:
            photo_dict = {'id': item['id'], 'likes': item['likes']['count']}
            photo_list.append(photo_dict)
        return sorted(photo_list, key=lambda d: d['likes'])[:3]


if __name__ == '__main__':
    load_dotenv()
    access_token = os.getenv('TOKEN2')
    user = VK(access_token)
    user_info = user.users_info('7312956')
    (birth_year, sex, city) = (user_info['birth_year'], user_info['sex'], user_info['city'])
    print(user.users_info('7312956'))
    pprint(user.photos_get('7312956'))
    sex = [2, 1][sex - 1]
    pprint(user.search_users(birth_year, sex, city))
