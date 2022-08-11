import os
from pprint import pprint
import requests
from dotenv import load_dotenv

from bot_auth import Auth

URL = 'https://api.vk.com/method/'


def users_info(vk_id: int, gr_params: dict, us_params: dict):
    """
            Функция получает id пользователя ВК и возвращает данные по нему в виде словаря


    :param vk_id
    :param gr_params: dict
    :param us_params: dict


    :return: user_dict_info { 'vk_id': int, 'first_name': srt, 'last_name': str, 'sex': int
                             'city_id': int, 'city':  str ,'birth_date': str, 'photos": str
                             }
    """

    params = {'user_ids': vk_id, 'fields': 'bdate, sex, city'}
    response = requests.get(f'{URL}users.get', params={**gr_params, **params}).json()
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
    params_photo = {'owner_id': vk_id, 'album_id': 'profile', 'extended': '1'}
    response1 = requests.get(f'{URL}photos.get', params={**us_params, **params_photo}).json()
    # pprint(response1)
    photo_list = []
    for item in response1['response']['items']:
        photo_dict = {'likes': item['likes']['count'] + item['likes']['user_likes'], 'photo_name': f"photo{item['owner_id']}_{item['id']}"}
        photo_list.append(photo_dict)
    long_name = ''
    for _photos in sorted(photo_list, key=lambda d: d['likes'], reverse=True)[:3]:
        long_name += f"{_photos['photo_name']},"
    user_dict_info['photos'] = long_name
    return user_dict_info


def search_users(user_dict_info: dict, us_params: str, offset=0):
    """
            Функция ищет кандидатов удовлетворяющих заданным условиям для
            поиска используется дополнительный ключ ['age']

    :param user_dict_info: { 'vk_id': int, 'first_name': srt, 'last_name': str, 'sex': int
                             'city_id': int, 'city':  str ,'birth_date': str, 'age': int , photos": str
                             }
    :type dict
    :param us_params параметр аутенфикации
    :var  {'response': {'count': int,
            'items': [{'can_access_closed': bool, 'first_name': str, 'id': int,
            'is_closed': bool, 'last_name': str', 'screen_name': str, 'track_code': long str}, ...,  ]}}

    :return json search_result
            [{'id': int, 'first_name': str, 'last_name': str}, ... ]
    """
    params = {'count': 100, 'offset': offset, 'city': user_dict_info['city_id'],
              'sex': {1:2,2:1,0:0}[user_dict_info['sex']], 'status': [1, 5, 6],
              'age from': user_dict_info['age'] - 5, 'age_to': user_dict_info['age'] + 5, 'has_photo': 1,
              'is_closed': False,
              'fields': ['photo', ' screen_name']
              }
    response = requests.get(f'{URL}users.search', params={**us_params, **params}).json()
    if response['response']['count'] >= 1000:
        pass
    # pprint(response)
    search_result = [{'id': x['id'], 'first_name': x['first_name'], 'last_name': x['last_name']}
                     for x in response['response']['items'] if x['is_closed'] is False]
    return search_result


if __name__ == '__main__':
    load_dotenv()
    user = Auth()
    # print(os.getenv('M_VK_ID'))
    # access_token = os.getenv('GROUP_TOKEN')
    # token = getting_tokens(os.getenv('VK_LOGIN'), os.getenv('VK_PASSWORD'), os.getenv('CLIENT_ID2'),
    #                       os.getenv('GROUP_ID2'))
    # access_user = os.getenv('USER_TOKEN_berson2005@yandex.ru')
    user = Auth()
    # print(user.__repr__())
    result = users_info(os.getenv('VK_ID'), user.gr_params, user.us_params)
    result['age'] = 35

    result2 = search_users(result, user.us_params)
    # print(users_info(os.getenv('N_VK_ID')), user.gr_params)
    pprint(result)
    pprint(result2)
