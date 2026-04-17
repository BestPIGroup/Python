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

leitura.drop(columns=['virtual_memory_total', 'virtual_memory_available'], inplace=True)

leitura.rename(columns={'disk_read_bytes' : 'disk_read_mbps', 'disk_write_bytes' : 'disk_write_mbps',
                   'net_bytes_sent' : 'net_mbps_sent', 'net_bytes_recv' : 'net_mbps_recv'}, inplace=True)

leitura['disk_read_mbps']=leitura['disk_read_mbps']/5
leitura['disk_write_mbps']=leitura['disk_write_mbps']/5
leitura['net_mbps_sent']=leitura['net_mbps_sent']/5
leitura['net_mbps_recv']=leitura['net_mbps_recv']/5

leitura['timestamp'] = datetime.strptime(leitura['timestamp'], "%Y-%m-%d %H:%M:%S")

leitura.to_csv('Python/leitura_escalavel.csv', index=False, encoding='utf-8')


