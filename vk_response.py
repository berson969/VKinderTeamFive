import requests
from datetime import datetime
import os


class Vk:

    def __init__(self, access_token, version='5.131'):
        self.token = access_token
        self.url = 'https://api.vk.com/method/'
        self.version = version
        self.params = {'access_token': self.token, 'v': self.version}

    def users_info(self, user_id):
        user_dict_info = {'age': '', 'sex': '', 'sity': ''}
        url_user_info = self.url+'users.get'
        params = {'user_ids': user_id, 'fields': 'bdate, sex, city'}
        response = requests.get(url_user_info, params={**self.params, **params}).json()
        if 'city' in response['response'][0]:
            user_dict_info['city'] = response['response'][0]['city']['title']
        else:
            user_dict_info['city'] = 'город не указан'

        if 'bdate' in response['response'][0]:
            if len(response['response'][0]['bdate'].split('.')) == 3:
                user_dict_info['age'] = str(datetime.now().year - int(response['response'][0]['bdate'].split('.')[-1]))
            else:
                user_dict_info['age'] = 'скрыт год рождения'
        else:
            user_dict_info['age'] = 'скрыта дата рождения'
        user_dict_info['sex'] = ['пол не указан', 'женский', 'мужской'][int(response['response'][0]['sex'])]

        return user_dict_info

    def photo_get(self, owner_id: str):
        photo_get_params = {
            'owner_id': owner_id,
            'album_id': 'profile',
            'extended': '1'
        }
        url_photo_get = self.url + 'photos.get?'
        return requests.get(url_photo_get, params={**self.params, **photo_get_params}).json()

access_token = os.getenv('TOKEN')
user_id = 'dubrovina_tatiana'
vk = Vk(access_token)
print(vk.users_info(user_id))
