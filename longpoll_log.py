from datetime import datetime

import requests

from bot_auth import Auth


def server_data(params):
    return requests.get('https://api.vk.com/method/messages.getLongPollServer',
                        params=params).json()['response']


def answer(params: dict):
    serv_data = server_data(params)
    while True:
        response = requests.get(
            f"https://{serv_data['server']}?act=a_check&key={serv_data['key']}"
            f"&ts={serv_data['ts']}&wait=90&mode=2&version=2").json()
        for elem in response['updates']:
            print(datetime.now().time(), elem)
        serv_data['ts'] = response['ts']


if __name__ == '__main__':
    process = Auth()
    answer(process.gr_params)
