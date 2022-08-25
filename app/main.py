import logging
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import chat
from database import Database
from config import VK_SESSION, ID_BOT
import time

logging.basicConfig(format="%(asctime)s: %(message)s", level=logging.INFO,
                    datefmt="%H:%M:%S")
longpoll = VkBotLongPoll(VK_SESSION, ID_BOT)

rooms_dict = {}


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


def main():
    try:
        chats = db.select_data("SELECT id_chat from chats")
        if len(chats) != 0:
            for room_id in chats:
                logging.info(f"Create chat with id: {int(room_id[0])}")
                rooms_dict[int(room_id[0])] = chat.Chat(room_id[0], db)

        for event in longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                chat_id = event.chat_id

                if chat_id not in rooms_dict:
                    try:
                        logging.info(f"Create the room with chat_id: {chat_id}")
                        rooms_dict[chat_id] = chat.Chat(event.chat_id, db)
                    except Exception as err:
                        logging.error(err)
                else:
                    logging.info("This room is exist.")

                if event.from_chat:
                    msg = event.object.message['text'].lower()
                    logging.info(f'User send info - {msg}')

                    user_id = event.object.message['from_id']
                    rooms_dict[chat_id].save_userid_in_db(user_id)

                    if msg == 'performance':
                        rooms_dict[chat_id].get_statics()
                    # Если у чела есть 300$ он может сделать performance:
                    # 1: stick finger - Увеличить поле counter_slave  тем самым сделать гаччи-жертву мз выбранного пользователя
                    # 2: cumming - Самим стать master
                    if 'stick finger in ass @' in msg:
                        slave_id = msg[msg.index('@') + 1:]
                        logging.info(f"user_id: {user_id} stick finger in ass {slave_id}")
                        rooms_dict[chat_id].make_performance(slave_id=slave_id, performance='stick')
                    # cumming in
                    elif 'cumming in @' in msg:
                        slave_id = msg[msg.index('@') + 1:]
                        logging.info(f"user_id: {user_id} cumming in {slave_id}")
                        rooms_dict[chat_id].make_performance(slave_id=slave_id, performance='cumming',
                                                             master_id=user_id)
                    elif 'кабачок' in msg:
                        rooms_dict[chat_id].get_len_dick()

    except Exception as error:
        logging.error(error)


if __name__ == '__main__':
    main()
