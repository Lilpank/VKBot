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
            self.users = list(self.users[0])

        scheduler = BackgroundScheduler()
        scheduler.add_job(self.choice_master_slave_from_db, 'cron', hour=10)
        # scheduler.add_job(self.choice_master_slave_from_db, 'interval', minutes=1)
        # scheduler.add_job(self.create_metrics, 'interval', minutes=10)
        scheduler.start()

        # self.get_statics()

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

    def update_count_in_db(self, artist_id, sign, value=1):
        count = self.db.select_data(
            f"select count_{sign} from participants where user_id='{artist_id}' and id_chat='{self.chat_id}' limit 1")[
                    0][
                    0] + value
        self.db.update_data(
            f"update participants set count_{sign}='{count}' where user_id='{artist_id}' and id_chat='{self.chat_id}'")

        logging.info(f"update count_{sign} in table participants with user_id={artist_id}, count_{sign}={count}")

    def choice_master_slave_from_db(self):
        while True:
            users_id = list(
                self.db.select_data(f"select distinct user_id from participants where id_chat='{self.chat_id}'"))
            if len(users_id) == 0:
                return
            slave_id = random.choice(users_id)

            self.update_count_in_db(int(slave_id[0]), 'slave')

            users_id.remove(slave_id)
            if len(users_id) == 0:
                return

            master_id = random.choice(users_id)[0]
            self.update_count_in_db(int(master_id), 'master')
            if len(users_id) == 0:
                return

    def create_metrics(self):
        self.metrics = self.db.select_data(
            f"select 'Master' as name, user_id, count_master as val  from participants p where id_chat={self.chat_id} "
            f"and count_master > count_slave union all select 'Slave' as name, user_id, count_slave as val "
            f" from participants p where id_chat={self.chat_id} and count_slave > count_master;")
    # TODO: Мне не нравится, что в статистике бота тегает, это может действовать пользователям на нервы
    def get_statics(self):
        self.create_metrics()
        if self.metrics is None:
            vk_bot.sender("Statistics this dungeon is empty", self.chat_id)
            return
        vk_bot.sender("Performance this dungeon", self.chat_id)

        for metric in self.metrics:
            vk_bot.sender(f'{metric[0]} @id{metric[1]}: {metric[2]}', self.chat_id)

    def make_performance(self, slave_id, performance, master_id=None):
        match performance:
            case 'stick':
                self.update_count_in_db(slave_id, 'slave')
            case 'cumming':
                self.update_count_in_db(master_id, 'master')
        self.create_metrics()

    def get_len_dick(self):
        vk_bot.sender(f'your dick is {random.randint(1, 20)} CM', self.chat_id)
