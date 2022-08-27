import logging

from config import VK_SESSION

logging.basicConfig(format="%(asctime)s: %(message)s", level=logging.INFO,
                    datefmt="%H:%M:%S")


def sender(text, chat_id):
    VK_SESSION.method('messages.send', {'chat_id': chat_id, 'message': text, 'random_id': 0})


def get_name_from_id(user_id):
    user = VK_SESSION.method("users.get", {"user_ids": user_id})
    return user[0]['first_name'] + ' ' + user[0]['last_name']
