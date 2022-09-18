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
API_HASH = os.getenv('API_HASH')
API_ID = os.getenv('API_ID')
PASSWORD_TG = os.getenv('PASSWORD_TG')
PHONE = os.getenv('PHONE')

VK_SESSION = vk_api.VkApi(token=ACCESS_TOKEN)
