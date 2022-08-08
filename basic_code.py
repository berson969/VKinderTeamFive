import sys
from pprint import pprint
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll
from vk_api.utils import get_random_id
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from users import users_info, search_users
from database import add_whitelist, add_blacklist, choose_favorites
from bot_auth import Auth


class SelectedIterator():
    """
       Класс, позволяющий итерировать данные из поиска
       выдает по одному пользователя за раз
       __next__ возвращает словарь вида значение 'id': int
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
            return selected['id'], self.count
        return False, False


class DatingBot(Auth):
    """
        Класс управляющий сообщениями бота VK
    """

    def __init__(self):

        super().__init__()
        self.selected_id = None
        self.count = None
        self.user_id = None
        self.event = None
        self.longpoll = VkBotLongPoll(self.vk_gr_session, group_id=self.group_id)

    def iteration(self, dict_info: dict):
        """
          Метод назначения итератора, служит для запуска итерирования
        :param dict_info: dict
        :param self._iter__next__()
        :return: None
        """
        response = search_users(dict_info, self.us_params)
        self._iter = SelectedIterator(response)


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
        self.vk_api_gr_access.messages.edit(peer_id=peer_id, message=message,
                                            conversation_message_id=conversation_message_id, attachment=attachment,
                                            keyboard=keyboard)

    def show_selected(self, user_id):
        """
                Метод формирует фото кандидата и отправляет сообщения в Bot


        :param user_id
         :var int

        :return: selected_dict_info ['id']
         :type dict
        """
        selected, count = next(self._iter)
        self.count = count
        if selected is False:
            keyboard = VkKeyboard(one_time=False, inline=False)
            keyboard.add_callback_button(label='Показать выбранных', color=VkKeyboardColor.POSITIVE,
                                         payload={"text": "chosen"})
            keyboard.add_callback_button(label='Закончить', color=VkKeyboardColor.SECONDARY,
                                         payload={'text': 'exit'})
            keyboard = keyboard.get_keyboard()
            self.write_msg(user_id, 'Анкеты закончились', keyboard)
            return False
        else:
            select_info = users_info(selected, self.gr_params, self.us_params)
            message = f"{select_info['first_name']} {select_info['last_name']}\nhttps://vk.com/id{selected}"
            attachment = select_info['photos']
            keyboard = VkKeyboard(one_time=False, inline=True)
            keyboard.add_callback_button(label='Нравится', color=VkKeyboardColor.POSITIVE,
                                         payload={"text": "add_whitelist"})
            keyboard.add_callback_button(label='Не нравится', color=VkKeyboardColor.NEGATIVE,
                                         payload={"text": "add_blacklist"})
            keyboard = keyboard.get_keyboard()
            self.write_msg(user_id, message, keyboard, attachment)
            return select_info

    def messagerBot(self):
        """
                Основная функция бота: диалог с пользователем

            :return  event.obj [{'user_id': int, 'peer_id': int,
                            'event_id': long str, 'payload': str {"cmd': 'search_users'}"
                             }]

            :return  {'client_info': {'button_actions': ['text', ... , ...],
                    'carousel': True, 'inline_keyboard': True, 'keyboard': True, 'lang_id': 0},
                    'message': {'attachments': list, 'conversation_message_id': int,
                    'date': datetime, 'from_id': int,
                    'fwd_messages': list, 'id': int,
                    'important': bool, 'is_hidden': bool, 'out': int,
                    'peer_id': int, 'random_id': int, 'text': 'dsvgdf'}}

        """
        for self.event in self.longpoll.listen():

            if self.event.type == VkBotEventType.MESSAGE_NEW and self.event.message['text']:
                response = self.event.message['text'].lower()
                self.vk_id = self.event.message['from_id']
                if response in  ['привет', 'hello', 'start', 'hi']:
                    user_dict_info = users_info(self.vk_id, self.gr_params, self.us_params)
                    keyboard_start = VkKeyboard(one_time=True, inline=False)
                    keyboard_start.add_callback_button(label='ДА, начать!', color=VkKeyboardColor.POSITIVE,
                                                       payload={'text': 'search'})
                    # self.conversation_message_id = self.event.obj.message['conversation_message_id']

                    message = f"Хай, {user_dict_info['first_name']}! Хочешь познакомиться?"
                    keyboard = keyboard_start.get_keyboard()
                    self.write_msg(self.vk_id, message, keyboard)
                    # pprint(self.event.obj)
                elif response == '/exit':
                    sys.exit()
                else:
                    self.write_msg(self.vk_id, 'Не поняла Вашего вопроса', [])

            elif self.event.type == VkBotEventType.MESSAGE_EVENT:

                if self.event.obj.payload['text'] == "search":
                    self.iteration(user_dict_info)
                    keyboard_show_selected = VkKeyboard(one_time=False, inline=False)
                    keyboard_show_selected.add_callback_button(label='Следующие', color=VkKeyboardColor.PRIMARY,
                                                               payload={'text': 'next'})
                    keyboard_show_selected.add_line()
                    keyboard_show_selected.add_callback_button(label='Показать выбранные',
                                                               color=VkKeyboardColor.POSITIVE,
                                                               payload={'text': 'chosen'})
                    keyboard_show_selected.add_callback_button(label='Закончить', color=VkKeyboardColor.SECONDARY,
                                                               payload={'text': 'exit'})
                    self.write_msg(self.vk_id, f'Готовим анкеты', keyboard_show_selected.get_keyboard())
                    self.write_msg(self.vk_id, f'Начинаем!!', {})
                    self.selected_dict_info = self.show_selected(self.vk_id)
                    # pprint(self.event.obj)

                elif self.event.obj.payload['text'] == "add_whitelist":
                    res = add_whitelist(user_dict_info, self.selected_dict_info)
                    print(res)
                    self.selected_dict_info = self.show_selected(self.vk_id)
                    # print()
                # Запрос 4
                elif self.event.obj.payload['text'] == "add_blacklist":
                    res = add_blacklist(user_dict_info, self.selected_dict_info['vk_id'])
                    print(res)
                    self.selected_dict_info = self.show_selected(self.vk_id)
                    # print()
                # запрос 5
                elif self.event.obj.payload['text'] == "next":
                    self.selected_id = self.show_selected(self.vk_id)
                    keyboard_show_selected = VkKeyboard(one_time=True, inline=False)
                    keyboard_show_selected.add_callback_button(label='Следующие', color=VkKeyboardColor.PRIMARY,
                                                               payload={'text': 'next'})
                    keyboard_show_selected.add_line()
                    keyboard_show_selected.add_callback_button(label='Показать выбранные',
                                                               color=VkKeyboardColor.POSITIVE,
                                                               payload={'text': 'chosen'})
                    keyboard_show_selected.add_callback_button(label='Закончить', color=VkKeyboardColor.SECONDARY,
                                                               payload={'text': 'exit'})
                    keyboard = keyboard_show_selected.get_keyboard()
                    self.write_msg(self.vk_id, f'Осталось {self.count} анкет', keyboard_show_selected.get_keyboard())
                    # print()
                # Запрос на выход
                elif self.event.obj.payload['text'] == "exit":
                    # keyboard_exit = sjson.dumps('{"buttons":[],"one_time":True}')
                    self.write_msg(self.vk_id, 'До новых встреч!!', {})
                # Показ анкет
                elif self.event.obj.payload['text'] == "chosen":
                    keyboard_chosen = VkKeyboard(one_time=True, inline=False)
                    keyboard_chosen.add_callback_button(label='Показать еще', color=VkKeyboardColor.PRIMARY,
                                                        payload={'text': 'next'})
                    keyboard_chosen.add_line()
                    keyboard_chosen.add_callback_button(label='Закончить',
                                                        color=VkKeyboardColor.SECONDARY,
                                                        payload={'text': 'exit'})
                    self.write_msg(self.vk_id, 'ВЫБРАННЫЕ АНКЕТЫ', keyboard_chosen.get_keyboard())
                    for selected in choose_favorites(self.vk_id):
                        keyboard_select = VkKeyboard(inline=True)
                        keyboard_select.add_openlink_button(label=f"https://vk.com/id{selected['id']}",
                                                            link=f"https://vk.com/id{selected['id']}")
                        self.write_msg(self.vk_id, f"{selected['first_name']}"
                                                   f" {selected['last_name']}", keyboard_select.get_keyboard(),
                                       selected['long_photo_name'])


if __name__ == '__main__':
    main_process = DatingBot()
    main_process.messagerBot()
