import requests
from datetime import datetime
import os
from dotenv import load_dotenv


class VK:

    def __init__(self, access_token, vk_token, version='5.131'):
        self.user_dict_info = {}
        self.URL = 'https://api.vk.com/method/'
        self.token = access_token
        self.vktoken = vk_token
        self.version = version
        self.params = {'access_token': self.token, 'v': self.version}

    def users_info(self, vk_id):
        self.params = {'access_token': self.token, 'v': self.version}
        params = {'user_ids': vk_id, 'fields': 'bdate, sex, city'}
        response = requests.get(f'{self.URL}users.get', params={**self.params, **params}).json()
        print(response)
        if 'deactivate' in response['response'][0].keys():
            self.user_dict_info['vk_id'] = response['response'][0]['id']
            self.user_dict_info['name'] = response['response'][0]['first_name'] + ' ' + response['response'][0]['last_name']
            if 'city' in response['response'][0].keys():
                self.user_dict_info['city'] = response['response'][0]['city']['title']
            else:
                self.user_dict_info['city'] = ''
            if 'bdate' in response['response'][0].keys():
                self.user_dict_info['birth_year'] = response['response'][0]['bdate']
            else:
                self.user_dict_info['birth_year'] = ''
            self.user_dict_info['sex'] = response['response'][0]['sex']
            return self.user_dict_info
        return False

    def users_photos(self, vk_id):
        self.params = {'access_token': self.vktoken, 'v': self.version}
        params = {'owner_id': vk_id, 'album_id': 'profile', 'extended': '1', 'photo_size': '1'}
        response1 = requests.get(f'{self.URL}photos.get', params={**self.params, **params}).json()
        print(response1)
        return self.user_dict_info




load_dotenv()
access_token = os.getenv('TOKEN')
vk_token = os.getenv('VKTOKEN')
# vk_id = '552934290'
vk_id = '249815131'
# vk_id = '214792702'

# vk_id = '7312956'
# vk_id = '-8231976'
# vk_id = 'mixail_dubrovin'
# user_id = 'mixail_dubrovin'
user = VK(access_token, vk_token)
print(user.users_info(vk_id))
print(user.users_photos(vk_id))
