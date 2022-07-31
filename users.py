import requests
import os
from dotenv import load_dotenv
from pprint import pprint

def _count_likes(response1):
    count_dict = {}
    for i, item in enumerate(response1['response']['items']):
        count_dict[i] = sum(item['likes'].values())
    return sorted(count_dict, key=count_dict.get, reverse=True)


class VK:

    def __init__(self, access_token, version='5.131'):
        self.user_dict_info = {}
        self.photos_list = []
        self.URL = 'https://api.vk.com/method/'
        self.token = access_token
        self.version = version
        self.params = {'access_token': self.token, 'v': self.version}

    def users_info(self, vk_id: str, length=3):
        self.length = length
        params = {'user_ids': vk_id, 'fields': 'bdate, sex, city'}
        response = requests.get(f'{self.URL}users.get', params={**self.params, **params}).json()
        # print(response)
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
                self.user_dict_info['city'] = ''
            if 'bdate' in response['response'][0].keys():
                self.user_dict_info['birth_year'] = response['response'][0]['bdate']
            else:
                self.user_dict_info['birth_year'] = ''
            self.user_dict_info['sex'] = response['response'][0]['sex']
        params1 = {'owner_id': vk_id, 'album_id': 'profile', 'extended': '1', 'photo_size': '1'}
        response1 = requests.get(f'{self.URL}photos.get', params={**self.params, **params1}).json()
        try:
            key_list = _count_likes(response1)
            pprint(response1)
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


if __name__ == '__main__':
    load_dotenv()
    access_token = os.getenv('TOKEN2')
    user = VK(access_token)
    print(user.users_info(os.getenv('N_VK_ID')))

