import psutil
import pandas as pd
import numpy
import csv
import os
import time
import math
from datetime import datetime

def conversao_kb(valor: int):
    return round(valor/(1024), 2)

raw_csv = "Python/raw.csv"
trusted_csv = "Python/trusted.csv"
client_csv = "Python/client.csv"


leitura = pd.read_csv(raw_csv, sep=";")

print(leitura.head())

leitura['virtual_memory_usage'] = 100*((leitura['virtual_memory_total'] - leitura['virtual_memory_available'])/leitura['virtual_memory_total'])

leitura.drop(columns=['virtual_memory_total', 'virtual_memory_available'], inplace=True)

leitura.rename(columns={'disk_read_bytes' : 'disk_read_kbps', 'disk_write_bytes' : 'disk_write_kbps',
                   'net_bytes_sent' : 'net_kbps_sent', 'net_bytes_recv' : 'net_kbps_recv'}, inplace=True)

leitura['disk_read_kbps']=conversao_kb(leitura['disk_read_kbps']/5)
leitura['disk_write_kbps']=conversao_kb(leitura['disk_write_kbps']/5)
leitura['net_kbps_sent']=conversao_kb(leitura['net_kbps_sent']/5)
leitura['net_kbps_recv']=conversao_kb(leitura['net_kbps_recv']/5)

leitura['timestamp'] = pd.to_datetime(leitura['timestamp'], format='%Y-%m-%d %H:%M:%S')
leitura['timestamp'] = leitura['timestamp'].dt.strftime('%d/%m/%Y %H:%M:%S')

leitura = leitura.reindex(columns=['user', 'id_mac', 'timestamp', 'cpu_percent', 'cpu_time_user', 'cpu_ctx_switches', 
                                   'processo_pid_max_cpu', 'processo_name_max_cpu', 'processo_cpu_percent_max_cpu', 
                                   'total_processos', 'virtual_memory_usage', 'disk_read_kbps', 'disk_write_kbps',
                                   'disk_write_kbps', 'net_kbps_recv', 'net_packets_sent', 'net_packets_recv', 
                                   'net_errin', 'net_errout', 'net_dropin', 'net_dropout', 'usuarios_logados'])
    



leitura.to_csv(trusted_csv, index=False, encoding='utf-8', mode = 'a', header =(not os.path.exists(trusted_csv)))

leitura['virtual_memory_status'] = pd.cut(leitura['virtual_memory_usage'], 
                         bins=[0, 35, 65, math.inf], 
                        labels=['baixo', 'medio', 'alto'])
leitura['cpu_percent_status'] = pd.cut(leitura['cpu_percent'], 
                         bins=[0, 35, 65, math.inf], 
                        labels=['baixo', 'medio', 'alto'])
leitura['processo_cpu_percent_status'] = pd.cut(leitura['processo_cpu_percent_max_cpu'], 
                         bins=[0, 35, 65, math.inf], 
                        labels=['baixo', 'medio', 'alto'])

def categorizar(valor):
    if valor == 0:
        return 'normal'
    else:
        return 'erro'

# Cria a nova coluna
leitura['net_status'] = (leitura['net_errin'] + leitura['net_errout'] + leitura['net_dropin'] + leitura['net_dropout']).apply(categorizar)

leitura.to_csv(client_csv, index=False, encoding='utf-8', mode = 'a', header = (not os.path.exists(client_csv)))
