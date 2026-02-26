import psutil
import time
import csv
from datetime import datetime

arquivo_csv = "monitoramento.csv"

with open(arquivo_csv, mode="a",encoding="utf-8") as file:
    writer = csv.writer(file, delimiter=";")

    while True:
        cpu = psutil.cpu_percent(interval=1)
        memoria = psutil.virtual_memory().percent
        disco = psutil.disk_usage('/').percent
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        print("CPU:", cpu, "%\n")
        print("Memória:", memoria, "%\n")
        print("Disco:", disco, "%\n")
        print("--------------------------------------------------")

        writer.writerow([timestamp, cpu, memoria, disco])
        file.flush()

        time.sleep(1)
        []