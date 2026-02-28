import psutil
import time
import csv
from datetime import datetime

def conversao_gb(valor: float):
    return valor/ (1024 ** 3)

arquivo_csv = "monitoramento.csv"

with open(arquivo_csv, mode="a",encoding="utf-8") as file:
    writer = csv.writer(file, delimiter=";")

    while True:
        cpu = psutil.cpu_percent(interval=1)
        memoria = psutil.virtual_memory()
        disco = psutil.disk_usage('/')
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        memoria_total_gb = conversao_gb(memoria.total)
        memoria_available_gb = conversao_gb(memoria.available)
        memoria_used_gb = conversao_gb(memoria.used)
        memoria_free_gb = conversao_gb(memoria.free)

        disco_total_gb = conversao_gb(disco.total)
        disco_used_gb = conversao_gb(disco.used)
        disco_free_gb = conversao_gb(disco.free)

        writer.writerow([timestamp, cpu, round(memoria_total_gb, 2), round(memoria_available_gb, 2), round(memoria_used_gb, 2), round(memoria_free_gb, 2), round(disco_total_gb, 2), round(disco_used_gb, 2), round(disco_free_gb, 2)])

        time.sleep(2)