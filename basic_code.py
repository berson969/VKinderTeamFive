from random import randrange

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

token = input('Token: vk1.a.ANHGekoIKtlw7E7M8_EwtAry5mib578GD9r9iTlUUaHq7rx5UNh73gTavegLnVQbUStxFnhBsPd3xbxvQIQnF6_78rJZsT2g3-Q4h5CKLZb8Cti94yYODyVPoBPjkfGfYw9hqMYLiBbBWXhrSJlRlo93EZRJdt9hp9tjgh4ukVEUgx63eh5mOcsiQ-Ra4Ilo ')

vk = vk_api.VkApi(token=token)
longpoll = VkLongPoll(vk)


def write_msg(user_id, message):
    vk.method('messages.send', {'user_id': user_id, 'message': message,  'random_id': randrange(10 ** 7),})


for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:

        if event.to_me:
            request = event.text

            if request == "привет":
                write_msg(event.user_id, f"Хай, {event.user_id}")
            elif request == "пока":
                write_msg(event.user_id, "Пока((")
            else:
                write_msg(event.user_id, "Не поняла вашего ответа...")
