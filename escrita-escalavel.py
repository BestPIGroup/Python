import psutil
import json
import csv
import time

with open("banco.json", "r", encoding="utf-8") as file:
    dados = json.load(file)

def coletar_cpu_percent(parametros):
    interval = parametros.get("interval", 1)
    return psutil.cpu_percent(interval=interval)

def coletar_disk_usage(parametros):
    path = parametros.get("path", "/")
    return psutil.disk_usage(path).percent

def coletar_virtual_memory(parametros):
    return psutil.virtual_memory().percent

coletores = {
    "cpu_percent": coletar_cpu_percent,
    "disk_usage": coletar_disk_usage,
    "virtual_memory": coletar_virtual_memory
}

resultados = {
        "cpu_percent": "",
        "disk_usage": "",
        "virtual_memory": ""
    }

for componente in dados["componentes"]:
    nome = componente["nome"]
    parametros = componente["parametros"]

    funcao = coletores.get(nome)
    valor = funcao(parametros)
    resultados[nome] = valor

arquivo_csv = "escalavel.csv"

with open(arquivo_csv, mode="w",  newline='', encoding="utf-8") as file:
        writer = csv.writer(file, delimiter=";")
        writer.writerow(["CPU", "DISCO", "MEMORIA"])

while True:

    linha_componentes = []

    for componente in dados["componentes"]:
        nome = componente["nome"]
        linha_componentes.append(resultados[nome])

    with open(arquivo_csv, mode="a",  newline='', encoding="utf-8") as file:
        writer = csv.writer(file, delimiter=";")
        writer.writerow([linha_componentes])

    print(linha_componentes)
    time.sleep(3)

