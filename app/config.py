import vk_api
import os
from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
USER = os.getenv('USER')
PASSWORD = os.getenv('PASSWORD')
HOST = os.getenv('HOST')
PORT = os.getenv('PORT')
DATABASE = os.getenv('DATABASE')
ID_BOT = os.getenv('ID_BOT')

VK_SESSION = vk_api.VkApi(token=ACCESS_TOKEN)
