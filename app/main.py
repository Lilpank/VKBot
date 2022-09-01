import logging
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import chat
from database import Database
from config import VK_SESSION, ID_BOT
import time
import vk_bot

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
                    if '.help' in msg:
                        vk_bot.sender(
                            f'Привет, это бот MasterAndSlave, я начисляю раз в день 300$, чтобы ты мог выполнить одну из этих команд:'
                            f' "cumming in @[тегнуть игрока]", чтобы стать master'
                            f' или можешь выполнить команду "stick finger in ass @[тегнуть игрока]", чтобы друга сделать slave-жертву. '
                            f' Команда "performance" отправляет статистику чата.',
                            chat_id)

                    logging.info(f'User send info - {msg}')
                    user_id = event.object.message['from_id']
                    rooms_dict[chat_id].save_userid_in_db(user_id)

                    if msg == 'performance':
                        rooms_dict[chat_id].get_statics()
                    if 'stick finger in ass [id' in msg:
                        _performance('stick', msg, user_id, chat_id)
                    elif 'cumming in [id' in msg:
                        _performance('cumming', msg, user_id, chat_id)
                    elif 'кабачок' in msg:
                        rooms_dict[chat_id].get_len_dick()

    except Exception as error:
        logging.error(error)


def _performance(command, msg, user_id, chat_id):
    slave_id = msg[msg.index('[id') + 3:msg.index('|')]
    logging.info(f"user_id: {user_id} making performance in {slave_id}")

    if user_id == int(slave_id) and command == 'stick':
        vk_bot.sender(f'Ты че ебобо в себя совать кабачок', chat_id)
        return
    elif user_id == int(slave_id) and command == 'cumming':
        vk_bot.sender(f'Ты че ебанулся чтоли ты в себя кончил', chat_id)
        return

    rooms_dict[chat_id].make_performance(user_id, slave_id=slave_id, performance=command)


if __name__ == '__main__':
    main()
