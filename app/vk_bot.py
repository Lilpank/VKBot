import logging
import threading
import time
import random

from database import Database
from config import VK_SESSION

logging.basicConfig(format="%(asctime)s: %(message)s", level=logging.INFO,
                    datefmt="%H:%M:%S")


class VkBot:
    def __init__(self, chat_id):
        logging.info("Create the vk-bot!")
        self.chat_id = chat_id
        self.db = Database()
        self.db.insert_value_into_table(f"INSERT INTO chats(id_chat) values('{chat_id}')"
                                        f" ON CONFLICT (id_chat) "
                                        f"DO NOTHING ")

        self.users = self.db.select_data(f"Select distinct user_id from participants where id_chat = {chat_id}")
        if len(self.users) != 0:
            self.users = self.users[0]
        thread = threading.Thread(target=self.choice_slave_from_db, args=(self.chat_id,))
        thread.start()

    def sender(self, text):
        VK_SESSION.method('messages.send', {'chat_id': self.chat_id, 'message': text, 'random_id': 0})

    def get_chat_id(self):
        return self.chat_id

    def save_userid_in_db(self, user_id):
        if user_id not in self.users:
            self.users.append(user_id)
            self.db.insert_value_into_table(
                f"INSERT INTO participants(id_chat, user_id) values('{self.chat_id}', '{user_id}') ")
            logging.info(f'user_id: {user_id} insert into database')
        else:
            logging.info(f'user_id: {user_id} exists in db')

        logging.info(f'users list: {self.users}')

    def choice_slave_from_db(self, chat_id):
        while True:
            time.sleep(500)

            users_id = self.db.select_data(f"select distinct user_id from participants where id_chat='{chat_id}'")
            user_id = random.choice(users_id)[0]
            count = self.db.select_data(
                f"select count from participants where user_id='{user_id}' and id_chat='{chat_id}' limit 1")[0][0] + 1

            self.db.update_data(
                f"update participants set count='{count}' where user_id='{user_id}' and id_chat='{chat_id}'")

            logging.debug(f"update count in table participants with user_id={user_id}, count={count}")
            self.sender(f'@id{user_id}, отличного дня! ')
