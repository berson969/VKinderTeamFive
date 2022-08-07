import os
import time
from pprint import pprint
from users import users_info, photos_get, search_users
from database import add_whitelist, add_blacklist
from bot_auth import Auth
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll
from vk_api.utils import get_random_id
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import json


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

        super().__init__(Auth)
        self.user_id = None
        self.event = None
        self.longpoll = VkBotLongPoll(self.vk_gr_session, group_id=self.group_id)

    def iteration(self, user_id: int):
        """
          Метод назначения итератора, служит для запуска итерирования
        :param user_id: int
        :param self._iter__next__()
        :return: None
        """
        response = search_users(user_id, self.gr_params, self.us_params)
        self._iter = SelectedIterator(response)
        self._iter.__iter__()

    def write_msg(self, user_id: int, message=None, keyboard=None, attachment=None):
        """
            Отправляет сообщения в бот VK
            :param user_id
            :type int
            :param message
            :type str
            :param attachment
            :type str
            :param keyboard
            :type json

            :return:  {'client_info': {'button_actions': ['text', ... , ...],
                     'carousel': True, 'inline_keyboard': True, 'keyboard': True, 'lang_id': 0},
                     'message': {'attachments': [], 'conversation_message_id': 460,
                     'date': 1659721395, 'from_id': 204323306,
                     'fwd_messages': [], 'id': 497,
                     'important': False, 'is_hidden': False, 'out': 0,
                      'peer_id': 204323306, 'random_id': 0, 'text': 'dsvgdf'}}

        """
        params = {'user_id': user_id,
                  'message': message,
                  'attachment': attachment,
                  'random_id': get_random_id(),
                  'keyboard': keyboard
                  }
        self.vk_gr_session.method('messages.send', params)

    def edit_msg(self, peer_id: int, conversation_message_id: int, message=None, keyboard=None, attachment=None):
        """
            Редактирует сообщения и клавиатуры в боте VK
            :param peer_id
            :type int
            :param message
            :type str
            :param conversation_message_id
            :type int
            :param attachment
            :type str
            :param keyboard
            :type: json
        """
        # params = {'peer_id': peer_id,
        #           'message': message,
        #           'conversation_message_id': conversation_message_id,
        #           'attachment': attachment,
        #           'keyboard': keyboard
        #           }
        self.vk_api_gr_access.messages.edit(peer_id=peer_id, message=message, conversation_message_id=conversation_message_id, attachment=attachment, keyboard=keyboard)

    def show_selected(self, user_id):
        """
                Метод формирует фото кандидата и отправляет сообщения в Bot

        :return: selected['id']
        :type int
        """
        selected, count = self._iter.__next__()
        if selected is False:
            # делаем сообщение что антекты закончились
            pass
        else:
            long_photo_name = ''
            for photo_name in photos_get(selected['id'], self.us_params):
                long_photo_name += photo_name['photo_name'] + ','
            message = f"{selected['first_name']} {selected['last_name']}\nhttps://vk.com/id{selected['id']}"
            attachment = long_photo_name
            keyboard = VkKeyboard(one_time=False, inline=True)
            keyboard.add_callback_button(label='Нравится', color=VkKeyboardColor.POSITIVE,
                                         payload={"text": "add_whitelist"})
            keyboard.add_callback_button(label='Не нравится', color=VkKeyboardColor.NEGATIVE,
                                         payload={"text": "add_blacklist"})
            keyboard.add_callback_button(label='Следующие', color=VkKeyboardColor.PRIMARY,
                                         payload={"text": "next"})
            keyboard = keyboard.get_keyboard()
            self.write_msg(user_id, message, keyboard, attachment)
            res = self.event.obj
            peer_id = self.event.obj['peer_id']
            conversation_message_id = self.conversation_message_id
            keyboard = VkKeyboard(one_time=False, inline=True)
            keyboard.add_callback_button(label='Нравится', color=VkKeyboardColor.POSITIVE,
                                         payload={"text": "add_whitelist"})
            keyboard.add_callback_button(label='Не нравится', color=VkKeyboardColor.NEGATIVE,
                                         payload={"text": "add_blacklist"})
            keyboard.add_callback_button(label='Следующие', color=VkKeyboardColor.PRIMARY, payload={"text": "next"})
            keyboard = keyboard.get_keyboard()
            self.edit_msg(peer_id, conversation_message_id, message, keyboard, attachment)
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

            if self.event.type == VkBotEventType.MESSAGE_NEW and self.event.obj.message['text']:
                # Запрос 1
                user_dict_info = users_info(self.event.message['from_id'], self.gr_params)
                keyboard_start = VkKeyboard(one_time=True, inline=False)
                keyboard_start.add_callback_button(label='Начать', color=VkKeyboardColor.POSITIVE,
                                                   payload={'text': 'search'})
                self.conversation_message_id = self.event.obj.message['conversation_message_id']
                self.user_id = self.event.message['from_id']
                message = f"Хай, {user_dict_info['first_name']}! Хочешь познакомиться?"
                keyboard = keyboard_start.get_keyboard()
                self.write_msg(self.user_id, message, keyboard)
                pprint(self.event.obj)
                peer_id = self.event.obj.message['peer_id']
                message = 'Начнем!'
                keyboard_show_selected = VkKeyboard(one_time=True, inline=False)
                keyboard_show_selected.add_callback_button(label='Следующие', color=VkKeyboardColor.PRIMARY,
                                                           payload={'text': 'next'})
                keyboard_show_selected.add_line()
                keyboard_show_selected.add_callback_button(label='Показать выбранные', color=VkKeyboardColor.POSITIVE,
                                                           payload={'text': 'next'})
                keyboard_show_selected.add_callback_button(label='Закончить', color=VkKeyboardColor.SECONDARY,
                                                           payload={'text': 'next'})
                keyboard = keyboard_show_selected.get_keyboard()
                self.edit_msg(peer_id, self.conversation_message_id, message, keyboard)


            elif self.event.type == VkBotEventType.MESSAGE_EVENT:
                # Запрос 2
                if self.event.obj.payload['text'] == "search":
                    self.iteration(self.user_id)
                    self.selected_id = self.show_selected(self.user_id)
                    pprint(self.event.obj)
                # Запрос 3
                elif self.event.obj.payload['text'] == "add_whitelist":
                    res = add_whitelist(self.event.obj.user_id, self.selected_id, self.gr_params, self.us_params)
                    print(res)
                    self.selected_id = self.show_selected(self.user_id)
                    # print()
                # Запрос 4
                elif self.event.obj.payload['text'] == "add_blacklist":
                    res = add_blacklist(self.event.obj.user_id, self.selected_id, self.gr_params, self.us_params)
                    print(res)
                    self.selected_id = self.show_selected(self.user_id)
                    # pprint()
                # запрос 5
                elif self.event.obj.payload['text'] == "next":
                    selected_id = self.show_selected(self.user_id)
                # Запрос на выход
                elif self.event.obj.payload['text'] == "Good buy":
                    message = 'До новых встреч!!'
                    keyboard = VkKeyboard(one_time=True, inline=False)
                    keyboard.add_button(label='', color=VkKeyboardColor.POSITIVE,
                                        payload={'button': []})
                    self.write_msg(self.user_id, message, keyboard.get_keyboard())


if __name__ == '__main__':
    main_process = DatingBot()
    main_process.messagerBot()
