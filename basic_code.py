import sys
from datetime import datetime
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll
from vk_api.utils import get_random_id
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

from users import users_info, search_users
from database import add_whitelist, add_blacklist, choose_favorites
from bot_auth import Auth


def keyboard_creator(flag):
    """
        Изготавливает клавиатуры на вход передается flag соответствующей клавиатуры

    :param flag: 'chosen', 'start'
    :return: keydoard
    """
    if flag == 'chosen':
        keyboard = VkKeyboard(inline=False, one_time=True)
        keyboard.add_callback_button(label='Показ следующих', color=VkKeyboardColor.PRIMARY,
                                     payload={"callback": "next"})
        keyboard.add_line()
        keyboard.add_callback_button(label='Показ выбранных', color=VkKeyboardColor.POSITIVE,
                                     payload={"callback": "chosen"})
        keyboard.add_callback_button(label='Закончить', color=VkKeyboardColor.SECONDARY,
                                     payload={"callback": "exit"})
        return keyboard.get_keyboard()
    elif flag == 'start':
        keyboard_start = VkKeyboard(one_time=False, inline=False)
        keyboard_start.add_callback_button(label='ДА, начать!',
                                           color=VkKeyboardColor.POSITIVE,
                                           payload={"callback": "search"})
        return keyboard_start.get_keyboard()


def write_msg(user_id: int, message=None, keyboard=None, attachment=None):
    """
        Отправляет сообщения в бот VK
        :param user_id
        :param message
        :param attachment
        :param keyboard

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
    main_process.vk_gr_session.method('messages.send', params)
    # pprint(event.obj)


def edit_msg(peer_id: int, conversation_message_id: int, message=None, keyboard=None, attachment=None):
    """
        Редактирует сообщения и клавиатуры в боте VK( у меня не работает(((
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
    main_process.vk_api_gr_access.messages.edit(peer_id=peer_id, message=message,
                                                conversation_message_id=conversation_message_id, attachment=attachment,
                                                keyboard=keyboard)


def _iter_selected(dict_info):
    """
            Метод инициализации итератора selected
    :param dict_info:
    :return: iterator _selected
    :return count: int количество обьектов к итераторе
    """
    selected = search_users(dict_info, main_process.us_params)
    count = len(selected)
    _selected = iter(selected)
    return _selected, count


def show_selected(vk_id: int, _selected):
    """
            Функция формирует фото кандидата и отправляет сообщения в Botб работает за счет итератора
            self.selected, в конце итерирования возвращает  False


    :param _selected
    :param vk_id
        :type int
    :return: select_info
        :type dict {'vk_id': int, 'first_name': str, 'last_name': str,
                    'sex': int, 'city_id': int, 'city':  str ,'birth_date': str,
                    'photos": str
              }
    :return False
    """
    try:
        selected_id = next(_selected)['id']
        select_info = users_info(selected_id, main_process.gr_params, main_process.us_params)
        message = f"{select_info['first_name']} {select_info['last_name']}\nhttps://vk.com/id{selected_id}"
        attachment = select_info['photos']
        keyboard = VkKeyboard(one_time=False, inline=True)
        keyboard.add_callback_button(label='Нравится', color=VkKeyboardColor.POSITIVE,
                                     payload={"callback": "add_whitelist"})
        keyboard.add_callback_button(label='Не нравится', color=VkKeyboardColor.NEGATIVE,
                                     payload={"callback": "add_blacklist"})
        # keyboard.add_line()
        # keyboard.add_callback_button(label='Следующие', color=VkKeyboardColor.PRIMARY,
        #                              payload={"callback": "next"})
        keyboard = keyboard.get_keyboard()
        write_msg(vk_id, message, keyboard, attachment)
        return select_info
    except StopIteration:
        write_msg(vk_id, 'Анкеты закончились ((', keyboard_creator())
        return False


def messagerBot():
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
    longpoll = VkBotLongPoll(main_process.vk_gr_session, group_id=main_process.group_id)
    for event in longpoll.listen():

        if event.type == VkBotEventType.MESSAGE_NEW:

            response = event.message['text'].lower()
            user_dict_info = users_info(event.message['from_id'], main_process.gr_params, main_process.us_params)
            # Стартовый запрос
            if response in ['привет', 'hello', 'start', 'hi', '/', 'ghbdtn']:

                write_msg(event.message['from_id'], f"Хай, {user_dict_info['first_name']}! Хочешь познакомиться?")
                if len(user_dict_info['birth_date'].split('.')) != 3:
                    write_msg(user_dict_info['vk_id'], "Сколько тебе лет?")
                    # print(event.obj)
                else:
                    age = int((datetime.now() - datetime.strptime(user_dict_info['birth_date'], "%d.%m.%Y")).days / 365)
                    user_dict_info['age'] = age
                    write_msg(event.message['from_id'], 'Начнем?', keyboard_creator('start'))

            # Запрос возраста    and int(response) in range(16,100) and event.message['from_id'] == cm_id
            elif response.isdigit() and int(response) in range(16, 99):
                user_dict_info['age'] = int(response)
                write_msg(event.message['from_id'], 'Начнем?', keyboard_creator('start'))
            elif response == '/exit':
                sys.exit()
            else:
                # print(event.obj)
                write_msg(event.message['from_id'], 'Не поняла Вашего вопроса', [])
        elif event.type == VkBotEventType.MESSAGE_EVENT:

            # Запрос на поиск по базe
            if event.obj.payload['callback'] == "search":
                _selected, count = _iter_selected(user_dict_info)
                selected_dict_info = show_selected(event.obj.peer_id, _selected)
                write_msg(event.obj.peer_id, f"Найдено  {count} анкет", keyboard_creator('chosen'))

            # Запрос на обработку белого листа
            elif event.obj.payload['callback'] == "add_whitelist":
                selected_dict_info = show_selected(event.obj.peer_id, _selected)
                res = add_whitelist(user_dict_info, selected_dict_info)
                print(res)

            # Запрос на обработку блеклиста
            elif event.obj.payload['callback'] == "add_blacklist":
                selected_dict_info = show_selected(event.obj.peer_id, _selected)
                res = add_blacklist(user_dict_info, selected_dict_info['vk_id'])
                print(res)

            # запрос на продолжение  вывод данных и окончание
            elif event.obj.payload['callback'] == "next":
                selected_dict_info = show_selected(event.obj.peer_id, _selected)
                write_msg((event.obj.peer_id), 'Продолжай!', keyboard_creator('chosen'))
            # Показ анкет
            elif event.obj.payload['callback'] == "chosen":
                write_msg(event.obj.peer_id, 'Подождите готовлю анкеты',
                          VkKeyboard(one_time=False).get_empty_keyboard())
                for selected in choose_favorites((event.obj.peer_id)):
                    keyboard_select = VkKeyboard(inline=True)
                    keyboard_select.add_openlink_button(label=f"https://vk.com/id{selected['id']}",
                                                        link=f"https://vk.com/id{selected['id']}")
                    write_msg(event.obj.peer_id, f"{selected['first_name']} {selected['last_name']}",
                              keyboard_select.get_keyboard(),
                              selected['photos'])
                write_msg(event.obj.peer_id, 'Продолжить поиск?', keyboard_creator('chosen'))
            # Запрос на выход
            elif event.obj.payload['callback'] == "exit":
                write_msg(event.obj.peer_id, 'До новых встреч!!', VkKeyboard(one_time=False).get_empty_keyboard())


if __name__ == '__main__':
    main_process = Auth()
    messagerBot()
