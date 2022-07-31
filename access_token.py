import requests
import json

# client_id = '249815131'
# client_id = '204323306'
# group_id = '214792702'
client_id = '8231976'
URL = 'https://oauth.vk.com/authorize'
params = {'client_id': client_id, 'redirect_uri': 'https://oauth.vk.com/blank.html', 'display': 'page', 'scope': 'photos', 'response_type': 'token', 'v': '5.131', 'state': '12345'}
response = requests.get(URL, params=params)
print(response.text)
# 'redirect_uri': 'http://example.com/callback'
# 'group_ids': group_id ,
# response = requests.get('https://oauth.vk.com/authorize?client_id=8231976&display=page&scope=photos&response_type=token&v=5.131').json()
# print(response)