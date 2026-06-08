import psutil
import json
import csv
import time
import boto3
import os
from datetime import datetime, timezone, timedelta
from getmac import get_mac_address
from dotenv import load_dotenv

load_dotenv()

client = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("aws_access_key_id"),
    aws_secret_access_key=os.getenv("aws_secret_access_key"),
    aws_session_token=os.getenv("aws_session_token")
)

bucket = os.getenv("bucket")

with open("banco_escrita.json", "r", encoding="utf-8") as file:
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
def coletar_top_3_processos_cpu(parametros):
    for p in psutil.process_iter(['cpu_percent']):
        p.info['cpu_percent']
    time.sleep(0.1)
    processos = list(psutil.process_iter(['pid', 'name', 'cpu_percent']))
    processos_ordenados = sorted(processos, key=lambda p: p.info['cpu_percent'] or 0, reverse=True)
    matriz_top3 = [[p.info['pid'], p.info['name'], p.info['cpu_percent']] for p in processos_ordenados[:3]]
    return matriz_top3

def coletar_top_3_processos_disco(parametros):
    IGNORAR = {'System'}

    snapshot1 = {}
    for p in psutil.process_iter(['pid', 'name', 'io_counters']):
        try:
            if p.info['name'] not in IGNORAR and p.info['io_counters']:
                snapshot1[p.info['pid']] = {
                    'name':        p.info['name'],
                    'write_bytes': p.info['io_counters'].write_bytes,
                    'handles':     p.num_handles()
                }
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    time.sleep(3)

    taxas = []
    for p in psutil.process_iter(['pid', 'name', 'io_counters']):
        try:
            pid = p.info['pid']
            if p.info['name'] not in IGNORAR and p.info['io_counters'] and pid in snapshot1:
                delta_write   = p.info['io_counters'].write_bytes - snapshot1[pid]['write_bytes']
                delta_handles = p.num_handles() - snapshot1[pid]['handles']
                taxas.append([pid, p.info['name'], delta_write, delta_handles])
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    taxas_ordenadas = sorted(taxas, key=lambda x: x[2], reverse=True)
    return taxas_ordenadas[:3]

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
# def coletar_arquivos_abertos(parametros):
#     arquivos_abertos_total = 0
#     for proc in psutil.process_iter(['pid', 'name']):
#         try:
#             arquvios_abertos_local = proc.open_files()
#             arquivos_abertos_total += len(arquvios_abertos_local)
#         except (psutil.AccessDenied, psutil.ZombieProcess,psutil.NoSuchProcess):
#             pass
#     return arquivos_abertos_total

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
"top_3_processos_cpu": coletar_top_3_processos_cpu,
"top_3_processos_disco": coletar_top_3_processos_disco,
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
# "arquivos_abertos": coletar_arquivos_abertos
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
"top_3_processos_cpu":"",
"top_3_processos_disco":"",
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
# "arquivos_abertos":""
}

nome_servidor = psutil.users()[0].name
mac_servidor = get_mac_address()
raw_csv = f"{mac_servidor.replace(":","_")}_"+datetime.now(timezone(timedelta(hours=-3))).strftime("%Y-%m-%d %H-%M-%S")+".csv"

lista_nomes = []

def escrita():

    raw_csv = f"{mac_servidor.replace(":","_")}_"+datetime.now(timezone(timedelta(hours=-3))).strftime("%Y-%m-%d %H-%M-%S")+".csv"

    for componentes in dados["componentes"]:
        lista_nomes.append(componentes["nome"])

    cabecalho = ["user", "id_mac", "timestamp"]
    cabecalho.extend(lista_nomes)

    with open(raw_csv, mode="w", newline='', encoding="utf-8") as file:
        writer = csv.writer(file, delimiter=";")
        writer.writerow(cabecalho)

    while (True):

        print(os.path.exists(raw_csv))

        if os.path.exists(raw_csv) == False:

            raw_csv = f"{mac_servidor.replace(":","_")}_"+datetime.now(timezone(timedelta(hours=-3))).strftime("%Y-%m-%d %H-%M-%S")+".csv"
            with open(raw_csv, mode="w",  newline='', encoding="utf-8") as file:
                writer = csv.writer(file, delimiter=";")
                writer.writerow(cabecalho)

            next

        else:

            lista_componentes = []

            for componentes in dados["componentes"]:
                nome = componentes["nome"]
                parametros = componentes["parametros"]
                funcao = coletores.get(nome)
                valor = funcao(parametros)
                resultados[nome] = valor
                lista_componentes.append(resultados[nome])

            timestamp = datetime.now(timezone(timedelta(hours=-3))).strftime("%Y-%m-%d %H:%M:%S")

            registro = [nome_servidor, mac_servidor, timestamp]
            registro.extend(lista_componentes)
            print(registro)

            with open(raw_csv, mode="a", newline='', encoding="utf-8") as file:
                writer = csv.writer(file, delimiter=";")
                writer.writerow(registro)

            num_linhas = 0

            with open(raw_csv, "r") as f:
                leitor = csv.reader(f)
                num_linhas = sum(1 for row in leitor)

            if(num_linhas == 11):
                client.upload_file(raw_csv, bucket, f"raw/{raw_csv}")
                os.remove(raw_csv)

            time.sleep(5)


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