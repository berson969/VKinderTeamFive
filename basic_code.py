import os
from users import VKclass
from bot_auth import Auth
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll
from vk_api.utils import get_random_id
from dotenv import load_dotenv
import vk_api
# from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import json

load_dotenv()
# token = os.getenv('GROUP_TOKEN_214815089')  # здесь сидит групповой токен
GROUP_ID = os.getenv('GROUP_ID2')


class DatingBot(Auth):
    """
        Класс управляющий сообщениями бота VK
    """

    def __init__(self):
        super().__init__("DatingBot")
        self.longpoll = VkBotLongPoll(self.vk_gr_session, group_id=GROUP_ID)


    def messagerBot(self):
        for self.event in self.longpoll.listen():
            if self.event.type == VkBotEventType.MESSAGE_NEW:
                # vk_id = event.message['from_id']
                # print(vk_id)
                user = VKclass()
                user_info = user.users_info(self.event.message['from_id'])
                params = {
                    'user_id': self.event.message['from_id'],
                    'message': f"Хай, {user_info['first_name']}",
                    'random_id': get_random_id()
                }
                self.write_msg(params)
                keyboard = self.make_keyboard()
                params = {'user_id': self.event.message['from_id'], 'message': 'Хочешь познакомиться?',
                          'random_id': get_random_id(), 'keyboard': keyboard}
                self.write_msg(params)

            elif self.event.type == VkBotEventType.MESSAGE_EVENT:
                if self.event.obj['payload']['cmd'] == "search_users":
                    response = user.search_users(user_info)
                    for selected in response:
                        long_photo_name = ''
                        for photo_name in user.photos_get(selected['id']):
                            long_photo_name += photo_name['photo_name'] + ','
                        long_photo_name.rstrip(',')
                        params = {   'user_id': self.event.message['from_id'],
                                     'message': f'{selected['first_name']} {selected['last_name']}\nhttps://vk.com/id{selected['id']}',
                                     'attachment' : long_photo_name,
                                     'random_id': get_random_id()
                                     'keyboard': self.make_keyboard1()}
                        self.write_msg(params)
                elif self.event.obj['payload']['cmd'] == "add_whitelist":


                elif self.event.obj['payload']['cmd'] == "add_blacklist":




    def write_msg(self, params):
        self.vk_gr_session.method('messages.send', params)

    def make_keyboard(self):
        self.settings = dict(one_time=True, inline=False)
        self.keyboard = VkKeyboard(**self.settings)
        payload = {"cmd": "search_users"}
        self.keyboard.add_callback_button(label='Ок, давай попробуем!', color=VkKeyboardColor.POSITIVE, payload=payload)
        self.keyboard.add_line()
        payload = None
        self.keyboard.add_callback_button(label='Нет, спасибо...', color=VkKeyboardColor.SECONDARY, payload=payload)
        return self.keyboard.get_keyboard()


    def make_keyboard1(self):
        self.settings = dict(one_time=False, inline=True)
        self.keyboard = VkKeyboard(**self.settings)
        payload = {"cmd": "add_whitelist"}
        self.keyboard.add_callback_button(label='Нравиться', color=VkKeyboardColor.POSITIVE, payload=payload)
        payload = None
        payload = {"cmd": "add_blacklist"}
        self.keyboard.add_callback_button(label='Не нравиться', color=VkKeyboardColor.PRIMARY, payload=payload)
        return self.keyboard.get_keyboard()


     # def create_info_selected(self):


if __name__ == '__main__':
    main_process = DatingBot()
    main_process.messagerBot()

# for event in longpoll.listen():
#     if event.type == VkBotEventType.MESSAGE_NEW:
#         # print ({
#         #             'user_id': event.message['from_id'],
#         #             'cmids': event.message['conversation_message_id'],
#         #             'text': event.message['text'],
#         #             'type': 'MESSAGE_NEW'
#         #         })
#         if event.message['from_id']:
#             request = event.message['text'].lower()
#             # print(request)
#             if request == "привет":
#                 write_msg(event.message['from_id'], f"Хай, {event.message['from_id']}")
#                 print(event.message['from_id'])
#
#                 settings = dict(one_time=False, inline=True)
#                 keyboard = VkKeyboard(**settings)
#                 payload = {"cmd": "add_whitelist"}
#                 payload1 = "{\"button\": \"" + "1" + "\"}"
#                 keyboard.add_callback_button(label='Ок Давай попробуем', payload=payload)  # color=VkKeyboardColor.POSITIVE,
#                 # payload=payload)
#                 keyboard.add_callback_button(label="Нет( В следующий раз...",
#                                              payload=payload1)  # , color=VkKeyboardColor.POSITIVE
#                 params = {'user_id': event.message['from_id'], 'message': 'проверка', 'random_id': 0,
#                           'keyboard': keyboard.get_keyboard(),
#                           'attachment': 'photo7312956_338860344,photo7312956_284358095,photo7312956_230180557'}  # , 'attachment': 'photo7312956_338860344,photo7312956_284358095,photo7312956_230180557'
#                 # params = {}
#                 # params['keyboard'] = keyboard.get_keyboard()
#                 print(keyboard.get_keyboard())
#                 print(params)
#
#                 vk_session.method('messages.send', params)  # event.from_user, get_random_id(), ,
#                 # print(VkBotEventType.sendMessageEventAnswer)
#     elif event.type == VkBotEventType.MESSAGE_EVENT:
#         print(event.object.items())
#         print(event.object.payload.get('cmd'))
#         if event.object.payload.get('cmd') == "add_whitelist":

# r = vk.messages.sendMessageEventAnswer(
#     event_id=event.object.event_id,
#     user_id=event.object.user_id,
#     peer_id=event.object.peer_id,
#     event_data=list(event.object.payload))
# print(event.obj.payload.items())


# event.type == VkBotEventType.MESSAGE_EVENT
# var = event.type == VkBotEventType.MESSAGE_NEW
# if event.to_me:
#     request = event.text.lower()
#     print(request)
#     if request == "привет":
#         write_msg(event.user_id, f"Хай, {event.user_id}")
#         print(event.message['from_id'])
#
#         settings = dict(one_time=False, inline=True)
#         start_button = VkKeyboard(**settings)
# params = {'user_id': int(event.user_id), 'message': 'Хочешь познакомиться?',
#           'random_id': get_random_id(), 'keyboard': start_button.get_keyboard(),
#           'attachment': 'photo7312956_338860344,photo7312956_284358095,photo7312956_230180557'}
# vk_session.method('messages,send', **params)
# keyboard = start_button.get_keyboard()
# params = {'user_id': str(event.user_id), 'message': 'Хочешь познакомиться?', 'random_id': get_random_id(), 'keyboard': start_button.get_keyboard() }
# vk_session.method('messages.send', params)
#
# elif request == "пока":
#     write_msg(event.user_id, "Пока((")
# else:
#     write_msg(event.user_id, "Не поняла вашего ответа...")
#     # params = {'user_id': str(event.user_id), 'message': 'Хочешь познакомиться?', 'random_id': randrange(10 ** 7), 'keyboard': start_button.get_keyboard()}
# vk_session.method('messages.send', **params)
# # keyboard_1()
# elif event.get('type') in CALLBACK_TYPES:
# r = vk_session.messages.sendMessageEventAnswer(
#     event_id=event.object.event_id,
#     user_id=event.object.user_id,
#     peer_id=event.object.peer_id,
#     event_data=json.dumps(event.object.payload))
# {"one_time":false,"inline":true,"buttons":[[{"color":"positive","action":{"type":"callback", "payload":"{\\"type\\":{\\"client_id\\":\\"7312956\\"}}"}}]]}
