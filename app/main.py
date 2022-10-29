import asyncio
import logging
import threading

from telethon import events, TelegramClient
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

from database import Database
from config import VK_SESSION, ID_BOT, API_HASH, API_ID
import time
import chat

logging.basicConfig(format="%(asctime)s: %(message)s", level=logging.INFO,
                    datefmt="%H:%M:%S")
longpoll = VkBotLongPoll(VK_SESSION, ID_BOT)


def _connection_to_db():
    while True:
        try:
            db = Database()
            break
        except Exception as err:
            logging.info("Doesn't connection to db")
            time.sleep(5)
    return db


rooms_dict = {}
db = _connection_to_db()
chats = db.select_data("SELECT id_chat from chats")
if len(chats) != 0:
    for room_id in chats:
        logging.info(f"Create chat with id: {int(room_id[0])}")
        rooms_dict[int(room_id[0])] = chat.Chat(room_id[0], db)


def main():
    import vk_bot

    try:
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
                    elif msg == 'кабачок':
                        rooms_dict[chat_id].get_len_dick()

    except Exception as error:
        logging.error(error)


def _performance(command, msg, user_id, chat_id):
    import vk_bot
    slave_id = msg[msg.index('[id') + 3:msg.index('|')]
    logging.info(f"user_id: {user_id} making performance in {slave_id}")

    if user_id == int(slave_id) and command == 'stick':
        vk_bot.sender(f'Ты че ебобо в себя совать кабачок', chat_id)
        return
    elif user_id == int(slave_id) and command == 'cumming':
        vk_bot.sender(f'Ты че ебанулся чтоли ты в себя кончил', chat_id)
        return

    rooms_dict[chat_id].make_performance(user_id, slave_id=slave_id, performance=command)


def send_message_from_neural_horo(chat_id, neural_horo):
    if neural_horo is not None:
        VK_SESSION.method('messages.send', {'chat_id': chat_id, 'message': neural_horo, 'random_id': 0})


async def send_message():
    loop = asyncio.new_event_loop()
    client = TelegramClient('sessiongachi', API_ID, API_HASH, loop=loop)
    await client.start()

    @client.on(events.NewMessage(chats='neural_horo'))
    async def handler_new_message(event):
        try:
            neural_horo = event.message.message

            for room_id in rooms_dict.keys():
                send_message_from_neural_horo(room_id, neural_horo)
        except Exception as e:
            print(e)

    await client.run_until_disconnected()


def go():
    asyncio.run(send_message())


threading.Thread(target=go).start()
if __name__ == '__main__':
    main()
