import psutil
import json
import csv
import time
from datetime import datetime

with open("banco.json", "r", encoding="utf-8") as file:
    dados = json.load(file)

cpu = psutil.cpu_percent(interval=1)
memoria = psutil.virtual_memory()
disco = psutil.disk_usage('/')

def conversao_gb(valor: float):
    return valor/ (1024 ** 3)

def coletar_cpu_percent(parametros):
    return cpu

def coletar_disk_usage_percent(parametros):
    return disco.percent

def coletar_virtual_memory_percent(parametros):
    return memoria.percent

def coletar_virtual_memory_total_gb(parametros):
     return round(conversao_gb(memoria.total))

def coleta_virtual_memory_available_gb(parametros):
     return round(conversao_gb(memoria.available))

def coleta_virtual_memory_used_gb(parametros):
     return round(conversao_gb(memoria.used))

def coleta_virtual_memory_free_gb(parametros):
     return round(conversao_gb(memoria.free))

def coleta_disk_total_gb(parametros):
     return round(conversao_gb(disco.total))

def coleta_disk_used_gb(parametros):
     return round(conversao_gb(disco.used))

def coleta_disk_free_gb(parametros):
     return round(conversao_gb(disco.free))

lista_componentes = []

coletores = {
    "cpu_percent": coletar_cpu_percent,
    "virtual_memory_total_gb":coletar_virtual_memory_total_gb,
    "virtual_memory_available_gb":coleta_virtual_memory_available_gb,
    "virtual_memory_used_gb":coleta_virtual_memory_used_gb,
    "virtual_memory_free_gb":coleta_virtual_memory_free_gb,
    "virtual_memory_percent": coletar_virtual_memory_percent,
    "disk_total_gb":coleta_disk_total_gb,
    "disk_used_gb": coleta_disk_used_gb,
    "disk_free_gb":coleta_disk_free_gb,
    "disk_percent": coletar_disk_usage_percent
}

resultados = {
        "cpu_percent": "",
        "virtual_memory_total_gb": "",
        "virtual_memory_available_gb": "",
        "virtual_memory_used_gb": "",
        "virtual_memory_free_gb": "",
        "virtual_memory_percent": "",
        "disk_total_gb": "",
        "disk_used_gb": "",
        "disk_free_gb": "",
        "disk_percent": ""
    }

for componentes in dados["componentes"]:
    nome = componentes["nome"]
    parametros = componentes["parametros"]
    funcao = coletores.get(nome)
    valor = funcao(parametros)
    resultados[nome] = valor
    lista_componentes.append(resultados[nome])

nome_servidor = "isa"

arquivo_csv = "escalavel.csv"

with open(arquivo_csv, mode="w",  newline='', encoding="utf-8") as file:
        writer = csv.writer(file, delimiter=";")
        writer.writerow(["Nome", " Data", " CPU(%)", " Mémoria-total", " Mémoria-livre", " Mémoria-used", " Mémoria-free", " Mémoria(%)", " Disco-total", " Disco-used", " Disco-free", " Disco(%)"])

for i in range(1, 41):

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(arquivo_csv, mode="a",  newline='', encoding="utf-8") as file:
        writer = csv.writer(file, delimiter=";")
        writer.writerow([nome_servidor, timestamp ,lista_componentes])

    print(lista_componentes)
    time.sleep(3)