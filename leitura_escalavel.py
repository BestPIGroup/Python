import psutil
import pandas as pd
import csv
import time
from datetime import datetime

def conversao_kb(valor: int):
    return round(valor/(1024), 2)

arquivo_csv = "escrita_escalavel.csv"

leitura = pd.read_csv('Python/escrita_escalavel.csv', sep=";")

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
    

leitura.to_csv('Python/leitura_escalavel.csv', index=False, encoding='utf-8')


