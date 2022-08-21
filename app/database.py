import psycopg2
import logging
from app.config import USER, PASSWORD, HOST, PORT, DATABASE

logging.basicConfig(format="%(asctime)s: %(message)s", level=logging.INFO,
                    datefmt="%H:%M:%S")


class Database:
    create_table_chats = '''CREATE TABLE IF NOT EXISTS chats
                                     (ID SERIAL PRIMARY KEY     NOT NULL,
                                     id_chat         TEXT    NOT NULL); '''

    create_table_participants = '''CREATE TABLE IF NOT EXISTS participants
                                         (ID SERIAL PRIMARY KEY  NOT NULL,
                                         id_chat         INT    NOT NULL,
                                         user_id         INT     NOT NULL,
                                         count           INT     DEFAULT 0
                                         ); '''

    def __init__(self):
        self.connection = psycopg2.connect(user=USER,
                                           password=PASSWORD,
                                           host=HOST,
                                           port=PORT,
                                           database=DATABASE)

        self.cursor = self.connection.cursor()

    def insert_value_into_table(self, query):
        self.cursor.execute(self.create_table_chats)
        self.cursor.execute(self.create_table_participants)
        self.cursor.execute(query)

        self.connection.commit()

    def select_data(self, select: str):
        if select is not None:
            self.cursor.execute(select)
            return self.cursor.fetchall()

        raise Exception("Не удалось выполнить sql запрос")

    def update_data(self, query):
        self.cursor.execute(query)
        self.connection.commit()

    def connection_close(self):
        self.cursor.close(), self.connection.close()
