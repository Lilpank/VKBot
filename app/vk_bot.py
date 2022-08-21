from app.config import VK_SESSION


class VkBot:
    def __init__(self, chat_id):
        print("\nСоздан объект бота!")
        self.chat_id = chat_id

    def sender(self, text):
        VK_SESSION.method('messages.send', {'chat_id': self.chat_id, 'message': text, 'random_id': 0})
