import requests
from datetime import datetime
import os
from dotenv import load_dotenv
from pprint import pprint


def _count_likes(response1, count_dict={}):
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

    def users_info(self, vk_id):
        params = {'user_ids': vk_id, 'fields': 'bdate, sex, city'}
        response = requests.get(f'{self.URL}users.get', params={**self.params, **params}).json()
        # print(response)
        if 'deactivate' in response['response'][0].keys():
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
        key_list = _count_likes(response1)
        for i in range(3):
            for result in response1['response']['items'][key_list[i]]['sizes']:
                if result['type'] == 'y':
                    self.user_dict_info[f'photo{i}'] = result['url']
        return self.user_dict_info


if __name__ == '__main__':
    load_dotenv()
    access_token = os.getenv('TOKEN2')
    # vk_id = '552934290' # test
    # vk_id = '249815131'  #liliya
    # vk_id = '214792702'
    vk_id = '611864369'  # leonid
    # vk_id = '7312956' #michail
    # vk_id = '-8231976' #vkinder2
    # vk_id = 'mixail_dubrovin'
    # user_id = 'mixail_dubrovin'
    user = VK(access_token)
    print(user.users_info(vk_id))

