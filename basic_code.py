from random import randrange
import os
from dotenv import load_dotenv
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from users import VK
load_dotenv()
token = os.getenv('TOKEN1') # токен1 - токен бота(сообщества), токен2 - токен пользователя
user = VK(os.getenv('TOKEN2')) # не знаю правильно или нет но без этого не работает поиск фотографий (возможно как то можно использовать TOKEN1)
vk = vk_api.VkApi(token=token)
longpoll = VkLongPoll(vk)


def write_msg(user_id, message):
    vk.method('messages.send', {'user_id': user_id, 'message': message,  'random_id': randrange(10 ** 7)})
 
def get_but(text, color):
    return {
        "action": {
            "type": "text",
            "payload": "{\"button\": \"" + "1" + "\"}",
            "label": f"{text}"
        },
        "color": f"{color}"
    }


def write_users_photo(user_id, photo_id):
    vk.method('messages.send', {'user_id': user_id, 'attachment': f'photo{event.user_id}_{photo_id}', 'random_id': randrange(10 ** 7)})


for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:

        if event.to_me:
            request = event.text.lower()

            if request == "привет":
                user_info = user.users_info(event.user_id)
                write_msg(event.user_id, f'{user_info}') # выводит информацию о пользователе.
                photo_list = user.photos_get(event.user_id) # создает список фотографий
                for photo in photo_list: # выводит фотографии
                    write_users_photo(event.user_id, photo['id'])
            elif request == "пока":
                write_msg(event.user_id, "Пока((")
            else:
                write_msg(event.user_id, "Не поняла вашего ответа...")
             
