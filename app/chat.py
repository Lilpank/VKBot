import logging
import random
from apscheduler.schedulers.background import BackgroundScheduler
import vk_bot

logging.basicConfig(format="%(asctime)s: %(message)s", level=logging.INFO,
                    datefmt="%H:%M:%S")


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
        # scheduler.add_job(self.choice_master_slave_from_db, 'cron', hour=10)
        scheduler.add_job(self.choice_master_slave_from_db, 'interval', minutes=1)
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

    def update_count_in_db(self, id, sign):
        count = self.db.select_data(
            f"select count_{sign} from participants where user_id='{id}' and id_chat='{self.chat_id}' limit 1")[0][
                    0] + 1
        self.db.update_data(
            f"update participants set count_{sign}='{count}' where user_id='{id}' and id_chat='{self.chat_id}'")
        logging.info(f"update count_{sign} in table participants with user_id={id}, count={count}")
        vk_bot.sender(f'@id{id}, {sign} дня ♂️♂️♂️ ', self.chat_id)

    def choice_master_slave_from_db(self):
        users_id = list(
            self.db.select_data(f"select distinct user_id from participants where id_chat='{self.chat_id}'")[0])
        if len(users_id) == 0:
            return
        slave_id = random.choice(users_id)

        self.update_count_in_db(slave_id, 'slave')
        users_id.remove(slave_id)
        if len(users_id) == 0:
            return

        master_id = random.choice(users_id)[0]
        self.update_count_in_db(master_id, 'master')
