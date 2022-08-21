import logging

from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

from app.config import VK_SESSION, ID_BOT
from app.database import Database
from app.vk_bot import VkBot

logging.basicConfig(format="%(asctime)s: %(message)s", level=logging.INFO,
                    datefmt="%H:%M:%S")
longpoll = VkBotLongPoll(VK_SESSION, ID_BOT)

chat_bot_class_dict = {}
db = Database()


def main():
    try:
        for event in longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                chat_id = event.chat_id

                if chat_id not in chat_bot_class_dict:
                    chat_bot_class_dict[chat_id] = VkBot(event.chat_id, db)

                if event.from_chat:
                    msg = event.object.message['text'].lower()
                    logging.info(f'Пользователь написал - {msg}')

                    user_id = event.object.message['from_id']
                    chat_bot_class_dict[chat_id].save_userid_in_db(user_id)
    except Exception as error:
        logging.error(error)

    db.connection_close()


if __name__ == '__main__':
    main()
