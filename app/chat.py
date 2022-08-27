import itertools
import logging
import random
from apscheduler.schedulers.background import BackgroundScheduler
import vk_bot

logging.basicConfig(format="%(asctime)s: %(message)s", level=logging.INFO,
                    datefmt="%H:%M:%S")


class Chat:
    def __init__(self, chat_id, db):
        self.metrics = None
        self.db = db
        self.chat_id = chat_id

        db.insert_value_into_table(f"INSERT INTO chats(id_chat) values('{chat_id}')"
                                   f"ON CONFLICT (id_chat)"
                                   f"DO NOTHING")

        self.users = db.select_data(f"Select distinct user_id from participants where id_chat = {chat_id}")

        if len(self.users) != 0:
            self.users = list(itertools.chain(*self.users))

        scheduler = BackgroundScheduler()
        scheduler.add_job(self.choice_master_and_slave_from_db, 'cron', hour=10)
        # scheduler.add_job(self.choice_master_and_slave_from_db, 'interval', minutes=1)
        # self.choice_master_and_slave_from_db()
        scheduler.add_job(self.create_metrics, 'interval', minutes=10)
        scheduler.start()

        # self.get_statics()

    def save_userid_in_db(self, user_id):
        if user_id not in self.users:
            self.users.append(user_id)
            self.db.insert_value_into_table(
                f"INSERT INTO participants(id_chat, user_id) values('{self.chat_id}', '{user_id}')")

            self.db.insert_value_into_table(
                f"INSERT INTO names(user_id, name) values('{user_id}', '{vk_bot.get_name_from_id(user_id)}')"
                f"ON CONFLICT (name)"
                f"DO NOTHING")

            logging.info(f'user_id: {user_id} insert into database')
        else:
            logging.info(f'user_id: {user_id} exists in db')

        logging.info(f'users list: {self.users}')

    def get_chat_id(self):
        return self.chat_id

    def update_count_in_db(self, artist_id, sign, value=1):
        count = self.db.select_data(
            f"select count_{sign} from participants where user_id='{artist_id}' and id_chat='{self.chat_id}' limit 1")[
                    0][
                    0] + value
        self.db.update_data(
            f"update participants set count_{sign}='{count}' where user_id='{artist_id}' and id_chat='{self.chat_id}'")

        logging.info(f"update count_{sign} in table participants with user_id={artist_id}, count_{sign}={count}")

    def choice_master_and_slave_from_db(self):
        users = list(
            self.db.select_data(f"select distinct user_id from participants where id_chat='{self.chat_id}'"))
        users = list(itertools.chain(*users))

        while True:
            if len(users) == 0:
                self.create_metrics()
                return

            users = self.assigned_master_or_slave(users)

    def assigned_master_or_slave(self, users):
        if len(users) == 0:
            self.create_metrics()
            return
        jabroni_id = random.choice(users)
        self.update_count_in_db(jabroni_id, random.choice(['slave', 'master']))
        vk_bot.sender(f'Jabroni: {jabroni_id}', self.chat_id)
        users.remove(jabroni_id)
        return users

    def create_metrics(self):
        self.metrics = self.db.select_data(
            f" select 'Master' as alias, name,  bucks  from participants p, names m"
            f" where id_chat={self.chat_id} and p.user_id=m.user_id and count_master > count_slave "
            f" union all select 'Slave' as alias, name, bucks "
            f" from participants p, names m where id_chat={self.chat_id} "
            f" and count_slave > count_master and p.user_id=m.user_id;")

    def get_statics(self):
        self.create_metrics()
        if self.metrics is None or len(self.metrics) == 0:
            logging.info(f'performance metrics: {self.metrics}')
            vk_bot.sender("Statistics this dungeon is empty", self.chat_id)
            return

        vk_bot.sender("Performance this dungeon", self.chat_id)

        for metric in self.metrics:
            vk_bot.sender(f'{metric[0]} {metric[1]}: have {metric[2]}$ ', self.chat_id)

    def make_performance(self, user_id, slave_id, performance):
        if int(slave_id) not in self.users:
            logging.info(f"{slave_id} not in dungeon")
            vk_bot.sender(f'{slave_id} not in dungeon', self.chat_id)
            return

        bucks = self.db.select_data(
            f"select bucks from participants where id_chat={self.chat_id} and user_id={user_id}")[0][0]

        if bucks < 300:
            logging.info("Недостаточно bucks для performance $$$")
            vk_bot.sender(f'Недостаточно bucks для performance $$$', self.chat_id)
            return

        bucks -= 300

        self.db.update_data(
            f"UPDATE participants "
            f"SET bucks='{bucks}' "
            f"WHERE user_id='{user_id}' "
            f"AND id_chat='{self.chat_id}'")

        match performance:
            case 'stick':
                self.update_count_in_db(slave_id, 'slave')
            case 'cumming':
                self.update_count_in_db(user_id, 'master')
        self.create_metrics()

    def get_len_dick(self):
        vk_bot.sender(f'your dick is {random.randint(1, 20)} CM', self.chat_id)
