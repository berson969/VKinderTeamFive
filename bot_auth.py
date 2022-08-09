# Документация библиотеки vk_api: https://github.com/python273/vk_api
# Официальная документация VK API по разделу сообщений: https://vk.com/dev/messages
# Получить токен: https://vkhost.github.io/

import vk_api  # использование VK API
from vk_api.utils import get_random_id  # снижение количества повторных отправок сообщения
from dotenv import load_dotenv  # загрузка информации из .env-файла
import os  # работа с файловой системой


class Auth:
    """
   Аутенфикационный класс  ВКонтакте

    """


    def __init__(self, version='5.131'):
        """
        Инициализация бота при помощи получения доступа к API ВКонтакте

        :param vk_us_session
        :param vk_gr_session

        :param vk_api_us_access
        :param vk_api_gr_access

        :var user_id
        :var group_id
        """
        load_dotenv()
        # self.version = version

        # self.vk_us_session = None
        # self.vk_gr_session = None

        self.gr_authorized = False
        self.us_authorized = False


        # авторизация
        self.vk_api_gr_access = self.do_group_auth()

        if self.vk_api_gr_access is not None:
            self.gr_authorized = True

        self.vk_api_us_access = self.do_user_auth()

        if self.vk_api_us_access is not None:
            self.us_authorized = True

        # получение id пользователя из файла настроек окружения .env в виде строки USER_ID="1234567890"

        self.us_id = os.getenv("VK_ID")
        self.group_id = os.getenv("GROUP_ID")

        # получение авторизационных параметров для запросов в VK API
        self.gr_params = {'access_token': self.gr_token, 'v': '5.131'}
        self.us_params = {'access_token': self.us_token, 'v': '5.131'}

    def __repr__(self):
        return f'group: {self.group_id}, user {self.us_id}tokens: {self.gr_token}{self.us_token}, sessions:{self.vk_gr_session}{self.vk_us_session}'

    def do_group_auth(self):
        """
        Авторизация  за группу или приложение
        Использует переменную, хранящуюся в файле настроек окружения .env в виде строки ACCESS_TOKEN="1q2w3e4r5t6y7u8i9o..."
        :return: возможность работать с API от имени группы или приложения
        """
        self.gr_token = os.getenv("GROUP_TOKEN")
        try:
            self.vk_gr_session = vk_api.VkApi(token=self.gr_token)
            return self.vk_gr_session.get_api()
        except Exception as error:
            print(error)
            return None

    def do_user_auth(self):
        """
        Авторизация за пользователя (не за группу или приложение)
        Использует переменную, хранящуюся в файле настроек окружения .env в виде строки ACCESS_TOKEN="1q2w3e4r5t6y7u8i9o..."
        :return: возможность работать с API
        """
        self.us_token = os.getenv("USER_TOKEN")
        try:
            self.vk_us_session = vk_api.VkApi(token=self.us_token)
            return self.vk_us_session.get_api()
        except Exception as error:
            print(error)
            return None

    def send_message(self, receiver_user_id: str = None, message_text: str = "тестовое сообщение"):
        """
        Отправка сообщения от лица авторизованного пользователя
        :param receiver_user_id: уникальный идентификатор получателя сообщения
        :param message_text: текст отправляемого сообщения
        """
        if not self.gr_authorized:
            print("Unauthorized. Check if GROUP_ACCESS_TOKEN is valid")
            return

        if not self.us_authorized:
            print("Unauthorized. Check if USER_ACCESS_TOKEN is valid")
            return

        # если не указан ID - берём значение по умолчанию, если таковое указано в .env-файле
        if receiver_user_id is None:
            receiver_user_id = self.us_id

        try:
            self.vk_api_us_access.messages.send(user_id=receiver_user_id, message=message_text, random_id=get_random_id())
            print(f"Сообщение отправлено для ID {receiver_user_id} с текстом: {message_text}")
        except Exception as error:
            print(error)


if __name__ == '__main__':
    auth = Auth()
    # auth.do_group_auth()
    # auth.do_user_auth()
    print(auth.__dir__())
    print(auth.__repr__())
    print(auth.vk_us_session)
    print(auth.vk_api_gr_access)
