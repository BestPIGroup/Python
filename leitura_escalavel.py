import psutil
import pandas as pd
import csv
import time
from datetime import datetime

def conversao_gb(valor: float):
    return valor/ (1024 ** 3)

arquivo_csv = "escrita_escalavel.csv"

leitura = pd.read_csv('Python/escrita_escalavel.csv')

leitura['virtual_memory_usage'] = 100*((leitura['virtual_memory_total'] - leitura['virtual_memory_available'])/leitura['virtual_memory_total'])

def categorizar_cpu_time_user(cpu_time_user):
    return 'betterRestart' if cpu_time_user >= 604800 else 'dontRestart'

leitura['shouldRestart'] = leitura['cpu_time_user'].apply(categorizar_cpu_time_user)