import psutil
import json
import csv
import time
from datetime import datetime

with open("Python/banco.json", "r", encoding="utf-8") as file:
    dados = json.load(file)

def conversao_gb(valor: float):
    return valor/ (1024 ** 3)

arquivo_csv = "escrita-escalavel.csv"

with open(arquivo_csv, mode="r",  newline='', encoding="utf-8") as file:
        reader = csv.reader(file, delimiter=";")
        reader.writerow(["Nome", " ID MAC", " Data", lista_nomes])
