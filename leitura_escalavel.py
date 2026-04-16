import psutil
import csv
import time
from datetime import datetime

def conversao_gb(valor: float):
    return valor/ (1024 ** 3)

arquivo_csv = "escrita_escalavel.csv"

with open(arquivo_csv, mode= "r") as file:
    leitura = csv.DictReader(file, delimiter=';', quotechar='|')

    first_line = next(leitura)

    
    cpu_ctx_switches = 0
    disk_read_mbps = 0
