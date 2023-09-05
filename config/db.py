from pymongo import MongoClient
from decouple import config

# Configuramos la cadena de conexión con las credenciales reales:
username = config('USERNAME')
password = config('PASSWORD')
cluster_url = config('CLUSTER_URL')

connection_string = f"mongodb+srv://{username}:{password}@{cluster_url}"
client = MongoClient(connection_string)