import datetime
from dateutil.parser import parse
import requests
import os
from dotenv import load_dotenv
from pprint import pprint
from bot_auth import Auth

URL = 'https://api.vk.com/method/'


def users_info(vk_id: int, gr_params):
    """
            Функция получает id пользователя ВК и возвращает данные по нему в виде словаря

    :param vk_id
    :type int
    :param gr_params параметр аутенфикации

    :return: user_dict_info { 'vk_id': int, 'first_name': srt, 'last_name': str, 'sex': int
                             'city_id': int, 'city':  str ,'birth_date': str
                             }
    """

    params = {'user_ids': vk_id, 'fields': 'bdate, sex, city'}
    response = requests.get(f'{URL}users.get', params={**gr_params, **params}).json()
    print(response)
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


def photos_get(vk_id: int, us_params):
    """
             Функция выводит список словарей состоящих из ID фотографии
            и количества лайков 3 самых популярных фотографий

    :param vk_id: id user VK
    :type us_params параметры аутенфикации

    :return: photo_list список словарей [ {'id': int, 'likes': int,
                'vk_id': int, 'photo_name': str (photo12345_12345)}, ... ,  ]
    """

    photo_list = []
    params = {'owner_id': vk_id, 'album_id': 'profile', 'extended': '1'}
    response = requests.get(f'{URL}photos.get', params={**us_params, **params}).json()
    # pprint(response)
    for item in response['response']['items']:
        photo_dict = {'id': item['id'], 'likes': item['likes']['count'] + item['likes']['user_likes'],
                      'vk_id': vk_id, 'photo_name': f"photo{item['owner_id']}_{item['id']}"}
        photo_list.append(photo_dict)
    return sorted(photo_list, key=lambda d: d['likes'])[:3]


def search_users(user_id: int, gr_params: str, us_params: str, offset=0):
    """
            Функция ищет кандидатов удовлетворяющих заданным условиям

    :type gr_params, us_params параметры аутенфикации
    :var  {'response': {'count': int,
            'items': [{'can_access_closed': bool, 'first_name': str, 'id': int,
            'is_closed': bool, 'last_name': str', 'screen_name': str, 'track_code': long str}, ...,  ]}}

    :return json search_result
            [{'id': int, 'first_name': str, 'last_name': str}, ... ]
    """
    dict_info = users_info(user_id, gr_params)
    if len(dict_info['birth_date']) < 8:
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
              'is_closed': False,
              'fields': ['photo', ' screen_name']
              }
    response = requests.get(f'{URL}users.search', params={**us_params, **params}).json()
    pprint(response)
    search_result = [{'id': x['id'], 'first_name': x['first_name'], 'last_name': x['last_name']} for x in
                     response['response']['items'] if x['is_closed'] == False]
    return search_result


if __name__ == '__main__':
    load_dotenv()
    # print(os.getenv('M_VK_ID'))
    # access_token = os.getenv('GROUP_TOKEN_214815089')
    # token = getting_tokens(os.getenv('VK_LOGIN'), os.getenv('VK_PASSWORD'), os.getenv('CLIENT_ID2'),
    #                       os.getenv('GROUP_ID2'))
    # access_user = os.getenv('USER_TOKEN_berson2005@yandex.ru')
    user = Auth()
    # print(user.__repr__())
    result = users_info(os.getenv('VK_ID'), user.gr_params)
    result1 = photos_get(result['vk_id'], user.us_params)
    result2 = search_users(os.getenv('VK_ID'), user.gr_params, user.us_params)
    # print(users_info(os.getenv('N_VK_ID')), user.gr_params)
    pprint(result)
