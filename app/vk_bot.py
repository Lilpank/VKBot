import logging

from telethon import TelegramClient, events

from config import VK_SESSION, API_ID, API_HASH, PASSWORD_TG, PHONE

logging.basicConfig(format="%(asctime)s: %(message)s", level=logging.INFO,
                    datefmt="%H:%M:%S")

chat = 'neural_horo'

with TelegramClient('sessiongachi', API_ID, API_HASH).start(phone=PHONE, password=PASSWORD_TG) as client:
    def send_message_from_neural_horo(chat_id, neural_horo):
        if neural_horo is not None:
            VK_SESSION.method('messages.send', {'chat_id': chat_id, 'message': neural_horo, 'random_id': 0})


    @client.on(events.NewMessage(chats=chat))
    async def handler_new_message(event):
        try:
            import main
            neural_horo = event.message.message
            for room_id in main.rooms_dict.keys():
                send_message_from_neural_horo(room_id, neural_horo)
        except Exception as e:
            print(e)

if __name__ == '__main__':
    client.start()
    client.run_until_disconnected()


def sender(text, chat_id):
    VK_SESSION.method('messages.send', {'chat_id': chat_id, 'message': text, 'random_id': 0})


def get_name_from_id(user_id):
    user = VK_SESSION.method("users.get", {"user_ids": user_id})
    return user[0]['first_name'] + ' ' + user[0]['last_name']
