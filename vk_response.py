import requests
from datetime import datetime
import os

class VK:

    def __init__(self, access_token, user_id, version='5.131'):
        self.token = access_token
        self.id = user_id
        self.version = version
        self.params = {'access_token': self.token, 'v': self.version}

    def users_info(self):
        user_dict_info = {'age': '', 'sex': '', 'sity': ''}
        url = 'https://api.vk.com/method/users.get'
        params = {'user_ids': self.id, 'fields': 'bdate, sex, city'}
        response = requests.get(url, params={**self.params, **params}).json()
        user_dict_info['city'] = response['response'][0]['city']['title']
        user_dict_info['age'] = datetime.now().year - int(response['response'][0]['bdate'].split('.')[2])
        user_dict_info['sex'] = ['пол не указан', 'женский', 'мужской'][int(response['response'][0]['sex'])]
        return user_dict_info

access_token = os.getenv('TOKEN')
user_id = 'mixail_dubrovin'
vk = VK(access_token, user_id)
print(vk.users_info())