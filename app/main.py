import logging
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from chat import Chat
from config import VK_SESSION, ID_BOT

logging.basicConfig(format="%(asctime)s: %(message)s", level=logging.INFO,
                    datefmt="%H:%M:%S")
longpoll = VkBotLongPoll(VK_SESSION, ID_BOT)

rooms_dict = {}


def main():
    try:
        for event in longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                chat_id = event.chat_id

                if chat_id not in rooms_dict:
                    try:
                        rooms_dict[chat_id] = Chat(event.chat_id)
                        logging.info(f"Create the room with chat_id: {chat_id}")
                    except Exception as err:
                        logging.error(err)
                if event.from_chat:
                    msg = event.object.message['text'].lower()
                    logging.info(f'User send info - {msg}')

                    user_id = event.object.message['from_id']
                    rooms_dict[chat_id].save_userid_in_db(user_id)
    except Exception as error:
        logging.error(error)


if __name__ == '__main__':
    main()
