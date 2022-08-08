import os
import vk_api
from dotenv import load_dotenv
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id

load_dotenv()
group_id = os.getenv('GROUP_ID')
user_id = os.getenv('VK_ID')
GROUP_TOKEN = os.getenv('GROUP_TOKEN')
USER_TOKEN = os.getenv('USER_TOKEN')
vk_gr = vk_api.VkApi(token=GROUP_TOKEN)
vk_user = vk_api.VkApi(token=USER_TOKEN)
vk_user_access = vk_user.get_api()

longpoll = VkBotLongPoll(vk_gr, group_id=group_id)
for event in longpoll.listen():

    if event.type == VkBotEventType.MESSAGE_NEW and event.obj.message['text']:
        # print(event.obj)
        key = VkKeyboard(one_time=True, inline=False)
        key.add_callback_button(label='Начать', color=VkKeyboardColor.POSITIVE,
                                payload={'text': 'search'})
        user_id = event.message['from_id']
        params = {'user_id': user_id,
                  'group_id': group_id,
                  'message': 'Hello',
                  'random_id': get_random_id(),
                  'keyboard': key.get_keyboard()
                  }
        cm_id = event.message['conversation_message_id']
        message_id = event.message['id']
        is_hidden = False
        vk_gr.method('messages.send', params)
        print(event.obj)

        keyboard = key.get_keyboard()
    #
    # elif event.type == VkBotEventType.MESSAGE_EVENT:
    #
    #     print(event.obj)

        peer_id = event.message['peer_id']
        # event_id = event.obj['event_id']
        key1 = VkKeyboard(one_time=True, inline=False)
        key1.add_callback_button(label='Начать', color=VkKeyboardColor.POSITIVE,
                                payload={'text': 'search'})
        keyboard = key1.get_keyboard()
        params = {
            'user_id': peer_id,
            'peer_id': peer_id,
            # 'group_id': group_id,
            'message_id': message_id,
            # 'event_id' : event_id,
            'message': 'Second time',
            # 'conversation_message_id': cm_id,
            # 'is_hidden': False,
            'keyboard': key.get_keyboard()
        }
        vk_gr.method('messages.edit', params)
        print(event.obj)
# peer_id = peer_id
#           'message': message,
#           'conversation_message_id': conversation_message_id,
#           'attachment': attachment,
#           'keyboard': keyboard
#           }
# vk_api_gr_access.messages.edit(peer_id=peer_id, message=message, conversation_message_id=conversation_message_id,
#                                     attachment=attachment, keyboard=keyboard)
#
#
# peer_id = self.event.obj.message['peer_id']
# message = 'Начнем!'
# keyboard_show_selected = VkKeyboard(one_time=True, inline=False)
# keyboard_show_selected.add_callback_button(label='Следующие', color=VkKeyboardColor.PRIMARY,
#                                            payload={'text': 'next'})
# keyboard_show_selected.add_line()
# keyboard_show_selected.add_callback_button(label='Показать выбранные', color=VkKeyboardColor.POSITIVE,
#                                            payload={'text': 'next'})
# keyboard_show_selected.add_callback_button(label='Закончить', color=VkKeyboardColor.SECONDARY,
#                                            payload={'text': 'next'})
# keyboard = keyboard_show_selected.get_keyboard()
# self.edit_msg(peer_id, self.conversation_message_id, message, keyboard)