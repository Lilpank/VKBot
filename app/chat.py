from app import vk_bot
from database import Database
import logging
import time
import threading
import random
import schedule

logging.basicConfig(format="%(asctime)s: %(message)s", level=logging.INFO,
                    datefmt="%H:%M:%S")


def _connection_to_db():
    while True:
        try:
            db = Database()
            break
        except Exception as err:
            logging.info("Doesn't connection to db")
            time.sleep(5)
    return db


db = _connection_to_db()


def choice_slave_from_db(chat_id):
    users_id = db.select_data(f"select distinct user_id from participants where id_chat='{chat_id}'")
    user_id = random.choice(users_id)[0]
    count = db.select_data(
        f"select count from participants where user_id='{user_id}' and id_chat='{chat_id}' limit 1")[0][0] + 1

    db.update_data(
        f"update participants set count='{count}' where user_id='{user_id}' and id_chat='{chat_id}'")

    logging.debug(f"update count in table participants with user_id={user_id}, count={count}")

    vk_bot.sender(f'@id{user_id}, отличного дня! ', chat_id)


class Chat:
    def __init__(self, chat_id):
        self.chat_id = chat_id

        db.insert_value_into_table(f"INSERT INTO chats(id_chat) values('{chat_id}')"
                                   f"ON CONFLICT (id_chat)"
                                   f"DO NOTHING")

        self.users = db.select_data(f"Select distinct user_id from participants where id_chat = {chat_id}")
        if len(self.users) != 0:
            self.users = self.users[0]

        schedule.every().day.at("8:30").do(choice_slave_from_db, self.chat_id)

        thread = threading.Thread(target=self._schledule_choice_slave)
        thread.start()

    def _schledule_choice_slave(self):
        while True:
            schedule.run_pending()

    def save_userid_in_db(self, user_id):
        if user_id not in self.users:
            self.users.append(user_id)
            db.insert_value_into_table(
                f"INSERT INTO participants(id_chat, user_id) values('{self.chat_id}', '{user_id}')")
            logging.info(f'user_id: {user_id} insert into database')
        else:
            logging.info(f'user_id: {user_id} exists in db')

        logging.info(f'users list: {self.users}')

    def get_chat_id(self):
        return self.chat_id
