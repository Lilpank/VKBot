from apscheduler.schedulers.background import BackgroundScheduler
import vk_bot
from database import Database
import logging
import time
import threading
import random

logging.basicConfig(format="%(asctime)s: %(message)s", level=logging.INFO,
                    datefmt="%H:%M:%S")

sched = BackgroundScheduler()


class Chat:
    def __init__(self, chat_id, db):
        self.db = db
        self.chat_id = chat_id

        db.insert_value_into_table(f"INSERT INTO chats(id_chat) values('{chat_id}')"
                                   f"ON CONFLICT (id_chat)"
                                   f"DO NOTHING")

        self.users = db.select_data(f"Select distinct user_id from participants where id_chat = {chat_id}")
        if len(self.users) != 0:
            self.users = list(self.users[0])

        scheduler = BackgroundScheduler()

        # scheduler.add_job(self.choice_slave_from_db, 'cron', hour=18, minute=24)
        scheduler.add_job(self.choice_slave_from_db, 'interval', minutes=1)
        scheduler.start()

    def save_userid_in_db(self, user_id):
        if user_id not in self.users:
            self.users.append(user_id)
            self.db.insert_value_into_table(
                f"INSERT INTO participants(id_chat, user_id) values('{self.chat_id}', '{user_id}')")
            logging.info(f'user_id: {user_id} insert into database')
        else:
            logging.info(f'user_id: {user_id} exists in db')

        logging.info(f'users list: {self.users}')

    def get_chat_id(self):
        return self.chat_id

    def choice_slave_from_db(self):
        users_id = self.db.select_data(f"select distinct user_id from participants where id_chat='{self.chat_id}'")
        user_id = random.choice(users_id)[0]
        count = self.db.select_data(
            f"select count from participants where user_id='{user_id}' and id_chat='{self.chat_id}' limit 1")[0][0] + 1

        self.db.update_data(
            f"update participants set count='{count}' where user_id='{user_id}' and id_chat='{self.chat_id}'")

        logging.info(f"update count in table participants with user_id={user_id}, count={count}")

        vk_bot.sender(f'@id{user_id}, отличного дня! ', self.chat_id)
