from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

from app.config import VK_SESSION, ID_BOT
from app.database import Database
from app.vk_bot import VkBot
import threading
import time
import logging
import random

logging.basicConfig(format="%(asctime)s: %(message)s", level=logging.INFO,
                    datefmt="%H:%M:%S")
longpoll = VkBotLongPoll(VK_SESSION, ID_BOT)

chat_bot_class_dict = {}

db = Database()
users = dict()


def save_userid_in_db(chat_id, user_id):
    if chat_id not in users:
        users[chat_id] = [user_id]
        db.insert_value_into_table(f'''INSERT INTO participants(id_chat, user_id) values('{chat_id}', '{user_id}')''')
        chat_bot_class_dict[chat_id].sender(f'user_id: {user_id} insert into database')
    elif user_id not in users[chat_id]:
        users[chat_id].append(user_id)
        db.insert_value_into_table(f'''INSERT INTO participants(id_chat, user_id) values('{chat_id}', '{user_id}')''')
        chat_bot_class_dict[chat_id].sender(f'user_id: {user_id} insert into database')
    else:
        chat_bot_class_dict[chat_id].sender(f'user_id: {user_id} exist in dict')

    logging.info(f"bot: {chat_bot_class_dict}, chat_id: {chat_id}")
    logging.info(f'users list: {users}')


def choice_slave_from_db(bot, chat_id):
    while True:
        time.sleep(200)

        users_id = db.select_data(f"select distinct user_id from participants where id_chat='{chat_id}'")
        user_id = random.choice(users_id)[0]
        count = db.select_data(
            f"select count from participants where user_id='{user_id}' and id_chat='{chat_id}' limit 1")[0][0] + 1

        db.update_data(f"update participants set count='{count}' where user_id='{user_id}' and id_chat='{chat_id}'")
        # bot.sender(f'@id{user_id}, отличного дня! ')


def main():
    try:
        for event in longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                chat_id = event.chat_id

                if chat_id not in chat_bot_class_dict:
                    chat_bot_class_dict[chat_id] = VkBot(event.chat_id)
                    db.insert_value_into_table(f''' INSERT INTO chats(id_chat) values('{chat_id}')''')
                    chat_bot_class_dict[chat_id].sender(f'chat_id: {chat_id} insert into database')
                    logging.info(f'chat dict: {chat_bot_class_dict}')

                    thread = threading.Thread(target=choice_slave_from_db, args=(chat_bot_class_dict[chat_id], chat_id))
                    thread.start()

                if event.from_chat:
                    msg = event.object.message['text'].lower()
                    logging.info(f'Пользователь написал - {msg}')

                    user_id = event.object.message['from_id']

                    save_userid_in_db(chat_id, user_id)
    except Exception as error:
        logging.error(error)

    db.connection_close()


if __name__ == '__main__':
    main()
