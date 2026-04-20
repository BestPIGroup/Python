import psutil
import json
import csv
import time
import boto3
import os
from datetime import datetime
from getmac import get_mac_address
from dotenv import load_dotenv

# load_dotenv()

# client = boto3.client(
#     's3',
#     aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID"),
#     aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY"),
#     aws_session_token = os.getenv("AWS_SESSION_TOKEN")
# )

with open("Python/banco_escrita.json", "r", encoding="utf-8") as file:
    dados = json.load(file)

def conversao_gb(valor: float):
    return valor / (1024 ** 3)

def coletar_cpu_percent(parametros):
    return round(psutil.cpu_percent(interval=1),2)
def coletar_cpu_count_logical(parametros):
    return round(psutil.cpu_count(),2)
def coletar_cpu_count_physical(parametros):
    return round(psutil.cpu_count(logical=False),2)
def coletar_cpu_freq_current(parametros):
    cpu = psutil.cpu_freq()
    return round(cpu.current,2)
def coletar_cpu_freq_min(parametros):
    cpu = psutil.cpu_freq()
    return round(cpu.min,2)
def coletar_cpu_freq_max(parametros):
    cpu = psutil.cpu_freq()
    return round(cpu.max,2)
def coletar_cpu_ctx_switches(parametros):
    global ctx_switches_global
    ctx_switches_local = psutil.cpu_stats().ctx_switches
    resposta = ctx_switches_local - ctx_switches_global
    ctx_switches_global = ctx_switches_local
    return resposta
def coletar_cpu_interrupts(parametros):
    stats = psutil.cpu_stats()
    return round(stats.interrupts,2)
def coletar_cpu_soft_interrupts(parametros):
    stats = psutil.cpu_stats()
    return round(stats.soft_interrupts,2)
def coletar_cpu_syscalls(parametros):
    stats = psutil.cpu_stats()
    return round(stats.syscalls,2)
def coletar_cpu_time_user(parametros):
    tempos = psutil.cpu_times()
    return round(tempos.user,2)
def coletar_cpu_time_system(parametros):
    tempos = psutil.cpu_times()
    return round(tempos.system,2)
def coletar_cpu_time_idle(parametros):
    tempos = psutil.cpu_times()
    return round(tempos.idle,2)
def coletar_virtual_memory_total(parametros):
    memoria = psutil.virtual_memory()
    return memoria.total
def coletar_virtual_memory_total_gb(parametros):
    memoria = psutil.virtual_memory()
    return round(conversao_gb(memoria.total),2)
def coletar_virtual_memory_available(parametros):
    memoria = psutil.virtual_memory()
    return memoria.available
def coletar_virtual_memory_available_gb(parametros):
    memoria = psutil.virtual_memory()
    return round(conversao_gb(memoria.available),2)
def coletar_virtual_memory_used_gb(parametros):
    memoria = psutil.virtual_memory()
    return round(conversao_gb(memoria.used),2)
def coletar_virtual_memory_free_gb(parametros):
    memoria = psutil.virtual_memory()
    return round(conversao_gb(memoria.free),2)
def coletar_virtual_memory_percent(parametros):
    memoria = psutil.virtual_memory()
    return round(memoria.percent,2)
def coletar_virtual_memory_active_gb(parametros):
    memoria = psutil.virtual_memory()
    return round(conversao_gb(memoria.active),2)
def coletar_virtual_memory_inactive_gb(parametros):
    memoria = psutil.virtual_memory()
    return round(conversao_gb(memoria.inactive),2)
def coletar_virtual_memory_buffers_gb(parametros):
    memoria = psutil.virtual_memory()
    return round(conversao_gb(memoria.buffers),2)
def coletar_virtual_memory_cached_gb(parametros):
    memoria = psutil.virtual_memory()
    return round(conversao_gb(memoria.cached),2)
def coletar_swap_total_gb(parametros):
    swap = psutil.swap_memory()
    return round(conversao_gb(swap.total),2)
def coletar_swap_used_gb(parametros):
    swap = psutil.swap_memory()
    return round(conversao_gb(swap.used),2)
def coletar_swap_free_gb(parametros):
    swap = psutil.swap_memory()
    return round(conversao_gb(swap.free),2)
def coletar_swap_percent(parametros):
    swap = psutil.swap_memory()
    return round(swap.percent,2)
def coletar_swap_sin_gb(parametros):
    swap = psutil.swap_memory()
    return round(conversao_gb(swap.sin),2)
def coletar_swap_sout_gb(parametros):
    swap = psutil.swap_memory()
    return round(conversao_gb(swap.sout),2)
def coletar_disk_percent(parametros):
    disco = psutil.disk_usage('/')
    return round(disco.percent,2)
def coletar_disk_total_gb(parametros):
    disco = psutil.disk_usage('/')
    return round(conversao_gb(disco.total),2)
def coletar_disk_used_gb(parametros):
    disco = psutil.disk_usage('/')
    return round(conversao_gb(disco.used),2)
def coletar_disk_free_gb(parametros):
    disco = psutil.disk_usage('/')
    return round(conversao_gb(disco.free),2)
def coletar_disk_read_count(parametros):
    disco = psutil.disk_io_counters()
    return disco.read_count
def coletar_disk_write_count(parametros):
    disco = psutil.disk_io_counters()
    return disco.write_count
def coletar_disk_read_bytes_gb(parametros):
    disco = psutil.disk_io_counters()
    return round(conversao_gb(disco.read_bytes),2)
def coletar_disk_read_bytes(parametros):
    global disk_read_bytes_global
    disk_read_bytes_local = psutil.disk_io_counters().read_bytes
    resposta = disk_read_bytes_local - disk_read_bytes_global
    disk_read_bytes_global = disk_read_bytes_local
    return resposta
def coletar_disk_write_bytes_gb(parametros):
    disco = psutil.disk_io_counters()
    return round(conversao_gb(disco.write_bytes),2)
def coletar_disk_write_bytes(parametros):
    global disk_write_bytes_global
    disk_write_bytes_local = psutil.disk_io_counters().write_bytes
    resposta = disk_write_bytes_local - disk_write_bytes_global
    disk_write_bytes_global = disk_write_bytes_local
    return resposta
def coletar_disk_read_time(parametros):
    disco = psutil.disk_io_counters()
    return disco.read_time
def coletar_disk_write_time(parametros):
    disco = psutil.disk_io_counters()
    return disco.write_time
def coletar_net_bytes_sent_gb(parametros):
    rede = psutil.net_io_counters()
    return round(conversao_gb(rede.bytes_sent),2)
def coletar_net_bytes_sent(parametros):
    global net_bytes_sent_global
    net_bytes_sent_local = psutil.net_io_counters().bytes_sent
    resposta = net_bytes_sent_local - net_bytes_sent_global
    net_bytes_sent_global = net_bytes_sent_local
    return resposta
def coletar_net_bytes_recv_gb(parametros):
    rede = psutil.net_io_counters()
    return round(conversao_gb(rede.bytes_recv),2)
def coletar_net_bytes_recv(parametros):
    global net_bytes_recv_global
    net_bytes_recv_local = psutil.net_io_counters().bytes_recv
    resposta = net_bytes_recv_local - net_bytes_recv_global
    net_bytes_recv_global = net_bytes_recv_local
    return resposta
def coletar_net_packets_sent(parametros):
    global net_packets_sent_global
    net_packets_sent_local = psutil.net_io_counters().packets_sent
    resposta = net_packets_sent_local - net_packets_sent_global
    net_packets_sent_global = net_packets_sent_local
    return resposta
def coletar_net_packets_recv(parametros):
    global net_packets_recv_global
    net_packets_recv_local = psutil.net_io_counters().packets_recv
    resposta = net_packets_recv_local - net_packets_recv_global
    net_packets_recv_global = net_packets_recv_local
    return resposta
def coletar_net_errin(parametros):
    global net_errin_global
    net_errin_local = psutil.net_io_counters().errin
    resposta = net_errin_local - net_errin_global
    net_errin_global = net_errin_local
    return resposta
def coletar_net_errout(parametros):
    global net_errout_global
    net_errout_local = psutil.net_io_counters().errout
    resposta = net_errout_local - net_errout_global
    net_errout_global = net_errout_local
    return resposta
def coletar_net_dropin(parametros):
    global net_dropin_global
    net_dropin_local = psutil.net_io_counters().dropin
    resposta = net_dropin_local - net_dropin_global
    net_dropin_global = net_dropin_local
    return resposta
def coletar_net_dropout(parametros):
    global net_dropout_global
    net_dropout_local = psutil.net_io_counters().dropout
    resposta = net_dropout_local - net_dropout_global
    net_dropout_global = net_dropout_local
    return resposta
def coletar_total_processos(parametros):
    return round(len(psutil.pids()),2)
def coletar_processo_pid_max_cpu(parametros):
    top_cpu = max(psutil.process_iter(['pid', 'name', 'cpu_percent']), 
              key=lambda p: p.info['cpu_percent'])
    return top_cpu.info['pid']
def coletar_processo_name_max_cpu(parametros):
    top_cpu = max(psutil.process_iter(['pid', 'name', 'cpu_percent']), 
              key=lambda p: p.info['cpu_percent'])
    return top_cpu.info['name']
def coletar_processo_cpu_percent_max_cpu(parametros):
    top_cpu = max(psutil.process_iter(['pid', 'name', 'cpu_percent']), 
              key=lambda p: p.info['cpu_percent'])
    return (top_cpu.info['cpu_percent'])/(psutil.cpu_count())
def coletar_usuarios_logados(parametros):
    return round(len(psutil.users()),2)
def coletar_boot_time(parametros):
    return round(psutil.boot_time(),2)
def coletar_uptime_segundos(parametros):
    return round(time.time() - psutil.boot_time(),2)
def coletar_uptime_minutos(parametros):
    return round((time.time() - psutil.boot_time())/60,2)
def coletar_uptime_horas(parametros):
    return round((time.time() - psutil.boot_time())/3600,2)
def coletar_total_particoes(parametros):
    particoes = psutil.disk_partitions()
    return round(len(particoes),2)
def coletar_total_conexoes(parametros):
    conexoes = psutil.net_connections()
    return round(len(conexoes),2)
def coletar_bateria_percent(parametros):
    bateria = psutil.sensors_battery()
    return round(bateria.percent,2)
def coletar_bateria_plugada(parametros):
    bateria = psutil.sensors_battery()
    return round(bateria.power_plugged,2)
def coletar_bateria_segundos_restantes(parametros):
    bateria = psutil.sensors_battery()
    return round(bateria.secsleft,2)

coletores = {
"cpu_percent": coletar_cpu_percent,
"cpu_count_logical": coletar_cpu_count_logical,
"cpu_count_physical": coletar_cpu_count_physical,
"cpu_freq_current": coletar_cpu_freq_current,
"cpu_freq_min": coletar_cpu_freq_min,
"cpu_freq_max": coletar_cpu_freq_max,
"cpu_ctx_switches": coletar_cpu_ctx_switches,
"cpu_interrupts": coletar_cpu_interrupts,
"cpu_soft_interrupts": coletar_cpu_soft_interrupts,
"cpu_syscalls": coletar_cpu_syscalls,
"cpu_time_user": coletar_cpu_time_user,
"cpu_time_system": coletar_cpu_time_system,
"cpu_time_idle": coletar_cpu_time_idle,
"virtual_memory_total": coletar_virtual_memory_total,
"virtual_memory_total_gb": coletar_virtual_memory_total_gb,
"virtual_memory_available": coletar_virtual_memory_available,
"virtual_memory_available_gb": coletar_virtual_memory_available_gb,
"virtual_memory_used_gb": coletar_virtual_memory_used_gb,
"virtual_memory_free_gb": coletar_virtual_memory_free_gb,
"virtual_memory_percent": coletar_virtual_memory_percent,
"virtual_memory_active_gb": coletar_virtual_memory_active_gb,
"virtual_memory_inactive_gb": coletar_virtual_memory_inactive_gb,
"virtual_memory_buffers_gb": coletar_virtual_memory_buffers_gb,
"virtual_memory_cached_gb": coletar_virtual_memory_cached_gb,
"swap_total_gb": coletar_swap_total_gb,
"swap_used_gb": coletar_swap_used_gb,
"swap_free_gb": coletar_swap_free_gb,
"swap_percent": coletar_swap_percent,
"swap_sin_gb": coletar_swap_sin_gb,
"swap_sout_gb": coletar_swap_sout_gb,
"disk_percent": coletar_disk_percent,
"disk_total_gb": coletar_disk_total_gb,
"disk_used_gb": coletar_disk_used_gb,
"disk_free_gb": coletar_disk_free_gb,
"disk_read_count": coletar_disk_read_count,
"disk_write_count": coletar_disk_write_count,
"disk_read_bytes_gb": coletar_disk_read_bytes_gb,
"disk_read_bytes": coletar_disk_read_bytes,
"disk_write_bytes_gb": coletar_disk_write_bytes_gb,
"disk_write_bytes": coletar_disk_write_bytes,
"disk_read_time": coletar_disk_read_time,
"disk_write_time": coletar_disk_write_time,
"net_bytes_sent_gb": coletar_net_bytes_sent_gb,
"net_bytes_sent": coletar_net_bytes_sent,
"net_bytes_recv_gb": coletar_net_bytes_recv_gb,
"net_bytes_recv": coletar_net_bytes_recv,
"net_packets_sent": coletar_net_packets_sent,
"net_packets_recv": coletar_net_packets_recv,
"net_errin": coletar_net_errin,
"net_errout": coletar_net_errout,
"net_dropin": coletar_net_dropin,
"net_dropout": coletar_net_dropout,
"total_processos": coletar_total_processos,
"processo_pid_max_cpu": coletar_processo_pid_max_cpu,
"processo_name_max_cpu": coletar_processo_name_max_cpu,
"processo_cpu_percent_max_cpu": coletar_processo_cpu_percent_max_cpu,
"usuarios_logados": coletar_usuarios_logados,
"boot_time": coletar_boot_time,
"uptime_segundos": coletar_uptime_segundos,
"uptime_minutos": coletar_uptime_minutos,
"uptime_horas": coletar_uptime_horas,
"total_particoes": coletar_total_particoes,
"total_conexoes": coletar_total_conexoes,
"bateria_percent": coletar_bateria_percent,
"bateria_plugada": coletar_bateria_plugada,
"bateria_segundos_restantes": coletar_bateria_segundos_restantes

}

resultados = {
"cpu_percent":"",
"cpu_count_logical":"",
"cpu_count_physical":"",
"cpu_freq_current":"",
"cpu_freq_min":"",
"cpu_freq_max":"",
"cpu_ctx_switches":"",
"cpu_interrupts":"",
"cpu_soft_interrupts":"",
"cpu_syscalls":"",
"cpu_time_user":"",
"cpu_time_system":"",
"cpu_time_idle":"",
"virtual_memory_total":"",
"virtual_memory_total_gb":"",
"virtual_memory_available":"",
"virtual_memory_available_gb":"",
"virtual_memory_used_gb":"",
"virtual_memory_free_gb":"",
"virtual_memory_percent":"",
"virtual_memory_active_gb":"",
"virtual_memory_inactive_gb":"",
"virtual_memory_buffers_gb":"",
"virtual_memory_cached_gb":"",
"swap_total_gb":"",
"swap_used_gb":"",
"swap_free_gb":"",
"swap_percent":"",
"swap_sin_gb":"",
"swap_sout_gb":"",
"disk_percent":"",
"disk_total_gb":"",
"disk_used_gb":"",
"disk_free_gb":"",
"disk_read_count":"",
"disk_write_count":"",
"disk_read_bytes_gb":"",
"disk_read_bytes":"",
"disk_write_bytes_gb":"",
"disk_write_bytes":"",
"disk_read_time":"",
"disk_write_time":"",
"net_bytes_sent_gb":"",
"net_bytes_sent":"",
"net_bytes_recv_gb":"",
"net_bytes_recv ":"",
"net_packets_sent":"",
"net_packets_recv":"",
"net_errin":"",
"net_errout":"",
"net_dropin":"",
"net_dropout":"",
"total_processos":"",
"processo_pid_max_cpu":"",
"processo_name_max_cpu":"",
"processo_cpu_percent_max_cpu":"",
"usuarios_logados":"",
"boot_time":"",
"uptime_segundos":"",
"uptime_minutos":"",
"uptime_horas":"",
"total_particoes":"",
"total_conexoes":"",
"bateria_percent":"",
"bateria_plugada":"",
"bateria_segundos_restantes":""

}

nome_servidor = psutil.users()[0].name
mac_servidor = get_mac_address()
raw_csv = "Python/raw.csv"

lista_nomes =[]

def escrita():

    for componentes in dados["componentes"]:
            lista_nomes.append(componentes["nome"])

    cabecalho=["user", "id_mac", "timestamp"]
    cabecalho.extend(lista_nomes)

    with open(raw_csv, mode="w",  newline='', encoding="utf-8") as file:
            writer = csv.writer(file, delimiter=";")
            writer.writerow(cabecalho)

    for i in range(1, 60):    

        lista_componentes = []

        for componentes in dados["componentes"]:
            nome = componentes["nome"]
            parametros = componentes["parametros"]
            funcao = coletores.get(nome)
            valor = funcao(parametros)
            resultados[nome] = valor
            lista_componentes.append(resultados[nome])

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        registro = [nome_servidor, mac_servidor, timestamp]
        registro.extend(lista_componentes)

        with open(raw_csv, mode="a",  newline='', encoding="utf-8") as file:
            writer = csv.writer(file, delimiter=";")
            writer.writerow(registro)

        print(registro)

        time.sleep(5)
    
    # client.upload_file(raw_csv, "s3-teste-python-2026.04.11", f"raw/dados_brutos{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}.csv")

    # os.remove(path = raw_csv)

    # escrita()

ctx_switches_global = psutil.cpu_stats().ctx_switches
disk_read_bytes_global = psutil.disk_io_counters().read_bytes
disk_write_bytes_global = psutil.disk_io_counters().write_bytes
net_bytes_sent_global = psutil.net_io_counters().bytes_sent
net_bytes_recv_global = psutil.net_io_counters().bytes_recv
net_packets_sent_global = psutil.net_io_counters().packets_sent
net_packets_recv_global = psutil.net_io_counters().packets_recv
net_errin_global = psutil.net_io_counters().errin
net_errout_global = psutil.net_io_counters().errout
net_dropin_global = psutil.net_io_counters().dropin
net_dropout_global = psutil.net_io_counters().dropout

escrita()
        