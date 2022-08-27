import psycopg2
import logging
from config import USER, PASSWORD, HOST, PORT, DATABASE

logging.basicConfig(format="%(asctime)s: %(message)s", level=logging.INFO,
                    datefmt="%H:%M:%S")


class Database:
    create_table_chats = '''CREATE TABLE IF NOT EXISTS chats
                                     (ID SERIAL PRIMARY KEY     NOT NULL,
                                     id_chat         TEXT       UNIQUE); '''

    create_table_participants = '''CREATE TABLE IF NOT EXISTS participants
                                         (ID SERIAL PRIMARY KEY  NOT NULL,
                                         id_chat         INT     NOT NULL,
                                         user_id         INT     NOT NULL,
                                         count_slave     INT     DEFAULT 0,
                                         count_master    INT     DEFAULT 0,
                                         bucks           INT     DEFAULT 0
                                         ); '''

    def __init__(self):
        self.connection = psycopg2.connect(user=USER,
                                           password=PASSWORD,
                                           host=HOST,
                                           port=PORT,
                                           database=DATABASE)

        cursor = self.connection.cursor()
        cursor.execute(self.create_table_chats)
        cursor.execute(self.create_table_participants)
        self.connection.commit()
        cursor.close()

    def insert_value_into_table(self, query):
        cursor = self.connection.cursor()
        cursor.execute(query)
        self.connection.commit()
        cursor.close()

    def select_data(self, select: str):
        if select is not None:
            cursor = self.connection.cursor()
            cursor.execute(select)
            return cursor.fetchall()
        else:
            raise Exception("Не удалось выполнить sql запрос")

    def update_data(self, query: str):
        if query is not None:
            cursor = self.connection.cursor()
            cursor.execute(query)
            self.connection.commit()
            cursor.close()
        else:
            raise Exception("Не удалось выполнить update запрос")

    def connection_close(self) -> None:
        self.connection.close()
