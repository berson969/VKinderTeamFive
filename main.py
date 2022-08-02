import basic_code
from database import add_blacklist, add_whitelist, choose_favorite, check_blacklist
from vk_response import VK
from users import VK
import requests
import os
from dotenv import load_dotenv
from pprint import pprint
from random import randrange
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import sqlalchemy as sq
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine, ForeignKeyConstraint
from sqlalchemy.orm import declarative_base, relationship, sessionmaker


load_dotenv()
token = os.getenv('TOKEN')

vk = vk_api.VkApi(token=token)
longpoll = VkLongPoll(vk)


def write_msg(user_id, message):
    vk.method('messages.send', {'user_id': user_id, 'message': message,  'random_id': randrange(10 ** 7),})


for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:

        if event.to_me:
            request = event.text.lower()

            if request == "привет":
                write_msg(event.user_id, f"Хай, {event.user_id}")
            elif request == "пока":
                write_msg(event.user_id, "пока ((")
            elif request == "поиск":
                if request =="да":
                    write_msg("функция search еще не написана")
                elif request == "нет": 
                    write_msg(event.user_id, "хорошо, поиск не включен")
                else: 
                    write_msg(event.user_id, "Не поняла вашего ответа, да или нет?")
            else:
                write_msg(event.user_id, "Не поняла вашего ответа...")
