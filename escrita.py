import psutil
import time
import csv
from datetime import datetime

def conversao_gb(valor: float):
    return valor/ (1024 ** 3)

nome = "isa"

arquivo_csv = "monitoramento.csv"

with open(arquivo_csv, mode="w",  newline='', encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Nome", " Data", " CPU(%)", " Mémoria-total", " Mémoria-livre", " Mémoria-used", " Mémoria-free", " Mémoria(%)", " Disco-total", " Disco-used", " Disco-free", " Disco(%)"])

for i in range (1, 41):
    cpu = psutil.cpu_percent(interval=1)
    memoria = psutil.virtual_memory()
    disco = psutil.disk_usage('/')
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    memoria_total_gb = conversao_gb(memoria.total)
    memoria_available_gb = conversao_gb(memoria.available)
    memoria_used_gb = conversao_gb(memoria.used)
    memoria_free_gb = conversao_gb(memoria.free)
    memoria_percent = memoria.percent
 
    disco_total_gb = conversao_gb(disco.total)
    disco_used_gb = conversao_gb(disco.used)
    disco_free_gb = conversao_gb(disco.free)
    disco_percent = disco.percent

    with open(arquivo_csv, mode="a",  newline='', encoding="utf-8") as file:
        writer = csv.writer(file, delimiter=";")
        writer.writerow([nome, timestamp, cpu, round(memoria_total_gb, 2), round(memoria_available_gb, 2), round(memoria_used_gb, 2), round(memoria_free_gb, 2), memoria_percent, round(disco_total_gb, 2), round(disco_used_gb, 2), round(disco_free_gb, 2), disco_percent])

    print(f"Nome: {nome} | Data: {timestamp} - CPU: {cpu}% | Mem: {memoria_percent}% | Disk: {disco_percent}%")

    time.sleep(5)