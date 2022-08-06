import os
from pprint import pprint
from users import VKclass
from database import add_whitelist, add_blacklist
from bot_auth import Auth
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll
from vk_api.utils import get_random_id
from dotenv import load_dotenv
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import json

load_dotenv()
GROUP_ID = os.getenv('GROUP_ID2')


class SelectedIterator():
    """
       Класс, позволяющий итерировать данные из поиска
       выдает по одному пользователя за раз
       __next__ возвращает словарь вида {'id': int, 'first_name': str, 'last_name': str}
    """
    def __init__(self, search_list):
        try:
            self.response = search_list
            self.count = len(self.response)
        except KeyError as kE:
            print(kE)

    def __iter__(self):
        return self

    def __next__(self):
        if self.count > 0:
            selected = self.response[self.count - 1]
            self.count -= 1
            return selected, self.count
        return False, False


class DatingBot(Auth):
    """
        Класс управляющий сообщениями бота VK
    """

    def __init__(self):
        super().__init__("DatingBot")
        self.event = None
        self.longpoll = VkBotLongPoll(self.vk_gr_session, group_id=GROUP_ID)
        self.user = VKclass()

    def iteration(self, user_id: int):
        """
          Фунция назначения итератора, служит для запуска итерирования
        :param user_id: int
        :return: None
        """
        response = self.user.search_users(user_id)
        self._iter = SelectedIterator(response)
        self._iter.__iter__()

    def make_keyboard0(self):  # start keyboard
        self.settings = dict(one_time=True, inline=False)
        self.keyboard = VkKeyboard(**self.settings)
        payload = {'text': 'search', 'type': 'text'}
        self.keyboard.add_callback_button(label='Ок, давай попробуем!', color=VkKeyboardColor.POSITIVE, payload=payload)
        self.keyboard.add_line()
        payload = {'text': 'go_back', 'type': 'text'}
        self.keyboard.add_callback_button(label='Нет, спасибо...', color=VkKeyboardColor.SECONDARY, payload=payload)
        return self.keyboard.get_keyboard()

    def make_keyboard1(self):  # keyboard under messages
        self.settings = dict(one_time=False, inline=True)
        self.keyboard = VkKeyboard(**self.settings)
        payload = {"type": "text", "text": "add_whitelist"}
        self.keyboard.add_callback_button(label='Нравится', color=VkKeyboardColor.POSITIVE, payload=payload)
        payload = {"type": "text", "text": "add_blacklist"}
        self.keyboard.add_callback_button(label='Не нравится', color=VkKeyboardColor.NEGATIVE, payload=payload)
        payload = {"type": "text", "text": "next"}
        self.keyboard.add_callback_button(label='Следующие', color=VkKeyboardColor.PRIMARY, payload=payload)
        return self.keyboard.get_keyboard()

    def make_keyboard2(self):  # start review users
        self.settings = dict(one_time=False, inline=False)
        self.keyboard = VkKeyboard(**self.settings)
        payload = {"type": "text", "text": "next"}
        self.keyboard.add_callback_button(label='Начать показ', color=VkKeyboardColor.POSITIVE, payload=payload)
        self.keyboard.add_line()
        payload = {"type": "text", "text": "buy buy"}
        self.keyboard.add_callback_button(label='Нет, в другой раз', color=VkKeyboardColor.SECONDARY, payload=payload)
        return self.keyboard.get_keyboard()

    def make_keyboard3(self):  # next menu
        self.settings = dict(one_time=False, inline=False)
        self.keyboard = VkKeyboard(**self.settings)
        payload = {"type": "text", "text": "next"}
        self.keyboard.add_callback_button(label='Показать следующие', color=VkKeyboardColor.POSITIVE, payload=payload)
        self.keyboard.add_line()
        payload = {"type": "text", "text": "choose_favorites"}
        self.keyboard.add_callback_button(label='Показать результат', color=VkKeyboardColor.PRIMARY, payload=payload)
        self.keyboard.add_line()
        payload = {"type": "snow_snackbar", "text": "До новых встреч!!"}  # "{\"text\": \"buy-buy\"}"
        self.keyboard.add_callback_button(label='Выйти', color=VkKeyboardColor.SECONDARY, payload=payload)
        return self.keyboard.get_keyboard()

    def make_keyboard4(self):  # exit
        self.settings = dict(one_time=False, inline=False)
        self.keyboard = VkKeyboard(**self.settings)
        payload = {"type": "show_snackbar", 'text': "До новых встреч"}
        self.keyboard.add_callback_button(label='До новых встреч!!', color=VkKeyboardColor.POSITIVE, payload=payload)
        return self.keyboard.get_keyboard()

    def show_selected(self, keyboard):
        selected, count = self._iter.__next__()
        long_photo_name = ''
        for photo_name in self.user.photos_get(selected['id']):
            long_photo_name += photo_name['photo_name'] + ','
        long_photo_name.rstrip(',')
        params = {
            'user_id': self.event.object['user_id'],
            'message': f"{selected['first_name']} {selected['last_name']}\nhttps://vk.com/id{selected['id']}",
            'attachment': long_photo_name,
            'random_id': get_random_id(),
            'keyboard': keyboard
            }
        self.write_msg(params)
        return selected['id']



    def messagerBot(self):
        """
                Основная функция бота: диалог с пользователем

        :intermediate return event.object: json  [{'user_id': int, 'peer_id': int,
                                                   'event_id': long str, 'payload': str {"cmd': 'search_users'}"
                                                   }]

        :return  {'client_info': {'button_actions': ['text', ... , ...],
                 'carousel': True, 'inline_keyboard': True, 'keyboard': True, 'lang_id': 0},
 'message': {'attachments': [], 'conversation_message_id': 460,
             'date': 1659721395, 'from_id': 204323306,
             'fwd_messages': [], 'id': 497,
             'important': False, 'is_hidden': False, 'out': 0,
             'peer_id': 204323306, 'random_id': 0, 'text': 'dsvgdf'}}

        """

        for self.event in self.longpoll.listen():


            if self.event.type == VkBotEventType.MESSAGE_NEW:

                vk_id = self.event.message['from_id']
                self.user_info = self.user.users_info(self.event.message['from_id'])
                params = {
                    'user_id': self.event.message['from_id'],
                    'message': f"Хай, {self.user_info['first_name']}",
                    'random_id': get_random_id()
                }
                self.write_msg(params)
                keyboard = self.make_keyboard0()
                params = {'user_id': self.event.message['from_id'], 'message': 'Хочешь познакомиться?',
                          'random_id': get_random_id(), 'keyboard': keyboard}
                self.write_msg(params)

            elif self.event.type == VkBotEventType.MESSAGE_EVENT:
 # asking about searching
                #             pprint(self.event.obj)
                if self.event.obj.payload['text'] == "search":
                    # pprint(self.event.obj)
         # iterator start
                    self.iteration(self.event.obj['user_id'])
                    params = {
                        'user_id': self.event.object['user_id'],
                        'message': f"Внимание! Найдены подходящие анкеты",
                        'random_id': get_random_id(),
                        'keyboard': self.make_keyboard2()
                    }
                    self.write_msg(params)
                    self.selected_id = self.show_selected(self.make_keyboard1())
                # next users after whitelist
                elif self.event.obj['payload']['text'] == "add_whitelist":
                    pprint(self.event.obj)
                    res = add_whitelist(self.event.obj['user_id'], self.selected_id)
                    print(res)
                    self.show_selected(self.make_keyboard1())
                # next users after blacklist
                elif self.event.obj['payload']['text'] == "add_blacklist":
                    res = add_blacklist(self.event.obj['user_id'], self.selected['id'])
                    print(res)
                    self.show_selected(self.make_keyboard1())
                # review next users
                elif self.event.obj['payload']['text'] == "next":
                    selected, count = self._iter.__next__()
                    self.selected_id = selected['id']
                    long_photo_name = ''
                    for photo_name in self.user.photos_get(self.selected['id']):
                        long_photo_name += photo_name['photo_name'] + ','
                    long_photo_name.rstrip(',')
                    # print(selected)
                    params = {
                        'user_id': self.event.object['user_id'],
                        'message': f"{selected['first_name']} {selected['last_name']}\nhttps://vk.com/id{selected['id']}",
                        'attachment': long_photo_name,
                        'random_id': get_random_id(),
                        'keyboard': self.make_keyboard1()
                    }
                    self.write_msg(params)
                # exit
                elif self.event.obj['payload']['text'] == "buy buy":
                    params = {
                        'user_id': self.event.object['user_id'],
                        'message': f"До новых встреч",
                        'random_id': get_random_id(),
                        'keyboard': self.make_keyboard4()
                    }
                    self.write_msg(params)
                    return

    def write_msg(self, params):
        """
          Отправляет сообщения в бот VK
        :param params: {
                        'user_id': int,
                        'message': str",
                        'attachment': str,
                        'random_id': get_random_id(),
                        'keyboard': self.make_keyboard()
                    }
        :return:  {'client_info': {'button_actions': ['text', ... , ...],
                 'carousel': True, 'inline_keyboard': True, 'keyboard': True, 'lang_id': 0},
 'message': {'attachments': [], 'conversation_message_id': 460,
             'date': 1659721395, 'from_id': 204323306,
             'fwd_messages': [], 'id': 497,
             'important': False, 'is_hidden': False, 'out': 0,
             'peer_id': 204323306, 'random_id': 0, 'text': 'dsvgdf'}}
        """
        self.vk_gr_session.method('messages.send', params)

    def edit_msg(self, params):
        """
        Редактирует сообщения и клавиатуры в боте VK
        :param params: {
                        'peer_id': int,
                        'message': str",
                        'conversation_message_id': str,
                        'attachment': str,
                        'keyboard': self.make_keyboard()
                        }
        :return:
        """
        self.vk_gr_session.method('messages.edit', params)




if __name__ == '__main__':
    main_process = DatingBot()
    main_process.messagerBot()
