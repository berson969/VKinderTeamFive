import datetime
from dateutil.parser import parse
import requests
import os
from dotenv import load_dotenv
from pprint import pprint
from bot_auth import Auth


URL = 'https://api.vk.com/method/'


class VKclass(Auth):
    """
            Класс для запросов и поиска users в базе данных VK. Аутентификация производится через базовый класс Auth

    """

    def __init__(self, version='5.131'):
        super().__init__('VKclass')
        self.gr_params = {'access_token': self.gr_token, 'v': version}
        self.us_params = {'access_token': self.us_token, 'v': version}

    def users_info(self, vk_id: int):

        '''
                Функция получает id пользователя ВК и возвращает данные по нему в виде словаря
        :param vk_id: id user VK
        :return: user_dict_info { 'vk_id': , 'first_name': , 'last_name': 'sex':
                                 'city_id': , 'city': ,'birth_date':
                                 }
        '''

        params = {'user_ids': vk_id, 'fields': 'bdate, sex, city'}
        response = requests.get(f'{URL}users.get', params={**self.gr_params, **params}).json()
        # print(response)
        if not response['response']:
            return False
        elif 'deactivated' in response['response'][0].keys():
            return False
        else:
            user_dict_info = {'vk_id': response['response'][0]['id'],
                              'first_name': response['response'][0]['first_name'],
                              'last_name': response['response'][0]['last_name'],
                              'sex': response['response'][0]['sex']
                              }
            if 'city' in response['response'][0].keys():
                user_dict_info['city_id'] = response['response'][0]['city']['id']
                user_dict_info['city'] = response['response'][0]['city']['title']
            else:
                user_dict_info['city_id'] = 0
                user_dict_info['city'] = ''
            if 'bdate' in response['response'][0].keys():
                user_dict_info['birth_date'] = response['response'][0]['bdate']
            else:
                user_dict_info['birth_date'] = ''
        return user_dict_info

    def photos_get(self, vk_id: int):
        """
                 Функция выводит список словарей состоящих из ID фотографии
                и количества лайков 3 самых популярных фотографий

        :param vk_id: id user VK
        :return: photo_list список словарей [ {'id': , 'likes': , 'photo_name': }, ... ,  ]
        """

        photo_list = []
        params = {'owner_id': vk_id, 'album_id': 'profile', 'extended': '1', 'photo_size': '1'}
        response = requests.get(f'{URL}photos.get', params={**self.us_params, **params}).json()
        # pprint(response)
        for item in response['response']['items']:
            photo_dict = {'id': item['id'], 'likes': item['likes']['count'] + item['likes']['user_likes'],
                          'photo_name': f"photo{item['owner_id']}_{item['id']}"}
            photo_list.append(photo_dict)
        return sorted(photo_list, key=lambda d: d['likes'])[:3]

    def search_users(self, dict_info, offset=0):
        if len(dict_info['birth_date']) != 10:
            age = 35
            # raise TypeError
        else:
            age = int((datetime.datetime.now() - parse(dict_info['birth_date'])).days / 365)
        if dict_info['sex'] == 1:
            sex_opposite = 2
            age -= 5
        elif dict_info['sex'] == 2:
            sex_opposite = 1
            age += 5
        else:
            sex_opposite = 0
        params = {'count': 10, 'offset': offset, 'city': dict_info['city_id'],
                  'sex': sex_opposite, 'status': [1, 5, 6],
                  'age from': age - 5, 'age_to': age + 5, 'has_photo': 1,
                  'fields': ['photo', ' screen_name']
                  }
        response = requests.get(f'{URL}users.search', params={**self.gr_params, **params}).json()
        return response


if __name__ == '__main__':
    load_dotenv()
    # print(os.getenv('M_VK_ID'))
    # access_token = os.getenv('GROUP_TOKEN_214815089')
    # token = getting_tokens(os.getenv('VK_LOGIN'), os.getenv('VK_PASSWORD'), os.getenv('CLIENT_ID2'),
    #                       os.getenv('GROUP_ID2'))
    # access_user = os.getenv('USER_TOKEN_berson2005@yandex.ru')
    user = VKclass()
    print(user.__repr__())
    result = user.users_info(os.getenv('M_VK_ID'))
    result1 = user.photos_get(result['vk_id'])
    # print(user.users_info(os.getenv('N_VK_ID')))
    # pprint(user.search_users( result))
    pprint(result1)
