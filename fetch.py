# PORTUGAL RADIATION PANEL (RADMAP)
# CODE: Pedro Lucas
# FILE: fetch.py

import requests
from datetime import datetime, timedelta
import json
import pandas as pd
import os
from pymongo import MongoClient
from dotenv import load_dotenv
import time
import coordinates

locals = []
info_local = []

# Load sensitive information
load_dotenv('.env')
host = os.getenv('MONGO_HOST')
user = os.getenv('MONGO_USER')
password = os.getenv('MONGO_PASSWORD')
database_name = os.getenv('MONGO_DATABASE')
collection_name = os.getenv('MONGO_COLLECTION')

# Conectar ao MongoDB
client = MongoClient(f"mongodb://{user}:{password}@{host}:27017/?authSource=admin")
db = client[database_name]
collection = db[collection_name]

def fetch():
    url = "https://radnet.apambiente.pt/ajax/dashboard/drawChart.php"

    data_inicio = datetime.now()
    data_fim = datetime.now()
    data_inicio = data_fim - timedelta(hours=2)

    data_inicio_str = data_inicio.strftime('%d/%m/%Y %H:%M')
    data_fim_str = data_fim.strftime('%d/%m/%Y %H:%M')

    params = {
        'txtDataReport_start': data_inicio_str,
        'txtDataReport_end': data_fim_str,
        'jsonEstacoesList': '[1652, 7251168, 1303, 1307, 7593370, 1305, 1201, 7593374, 1311, 1302, 1404, 1310, 1552, 2711862, 1351, 1501, 7593377, 1306, 2711807, 1309, 1304, 1308, 7593380, 1252, 7251171, 1651]'
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        try:
            data = response.json()
            info = json.dumps(data)
            return info, data_inicio_str, data_fim_str

        except ValueError:
            print("Erro ao converter resposta para JSON.")
    else:
        print(f"Erro na requisição: {response.status_code}")

def store(hour, place, value, latitude, longitude):
    # Verifica se o valor jÃ¡ existe no MongoDB
    existing_data = collection.find_one({"value": value, "place": place, "hour": hour})
    
    if not existing_data:
        # Cria o documento a ser inserido
        radioactivity_data = {
            "hour": hour,
            "place": place,
            "value": float(value),
            "latitude": latitude,
            "longitude": longitude
        }
        # Insere o documento no MongoDB
        collection.insert_one(radioactivity_data)

def data_processing():
    info, hour_init, hour_end = fetch()
    data = json.loads(info)
    
    # Save data to JSON file
    """
    with open('data/dados.json', 'w') as f:
        json.dump(data, f, indent=4)
    """

    for i in range(len(data)):
        locals.append(data[i]["label"])
        info_local.append(data[i]["data"][int(len(data[i]["data"])) - 1][1])

    print(hour_init)
    print(hour_end)
    print(locals)
    print(info_local)
    i = 0
    for local in locals:
        j = 0
        # Retrieve coordinates from the dictionary
        latitude_value, longitude_value = coordinates.coordinates[local]
        value = info_local[i]
        for place in coordinates.coordinates:
            if place == local:
                new_place_name = coordinates.indexed[j]
                break
            if not (latitude_value and longitude_value):
                print(f"Coordinates not found for {local}")
            j += 1
        store(hour_init, new_place_name, value, latitude_value, longitude_value)
        i += 1
        time.sleep(0.2)
        
# Executa o processamento dos dados
# data_processing()