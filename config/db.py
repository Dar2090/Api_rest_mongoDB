from pymongo import MongoClient

from dotenv import load_dotenv
import os

load_dotenv()

# Configuramos la cadena de conexión con las credenciales reales:
user_name = os.getenv('USER')
password = os.getenv('PASSWORD')
cluster_url = os.getenv('CLUSTER_URL')

connection_string = f"mongodb+srv://{user_name}:{password}@{cluster_url}"
client = MongoClient(connection_string)

print(user_name)