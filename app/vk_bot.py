import logging

from config import VK_SESSION

logging.basicConfig(format="%(asctime)s: %(message)s", level=logging.INFO,
                    datefmt="%H:%M:%S")


def sender(text, chat_id):
    VK_SESSION.method('messages.send', {'chat_id': chat_id, 'message': text, 'random_id': 0})
