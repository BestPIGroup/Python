from dotenv import load_dotenv
import pandas as pd
import csv
import os
import math
import mysql.connector
from datetime import datetime
import boto3
from botocore.exceptions import ClientError

load_dotenv()

client = boto3.client(

    "s3",
    aws_access_key_id=os.getenv("aws_access_key_id"),
    aws_secret_access_key=os.getenv("aws_secret_access_key"),
    aws_session_token=os.getenv("aws_session_token")
)

print(os.getenv("aws_access_key_id"))
print(os.getenv("aws_secret_access_key"))
print(os.getenv("aws_session_token"))
print(os.getenv("bucket"))

bucket = os.getenv("bucket")

def pesquisarComponente(nome,mac):

    try:

        db = mysql.connector.connect(
        host= os.getenv("host"),
        user= os.getenv("user"),
        password= os.getenv("password"),
        database= os.getenv("database")
        )

        cursor = db.cursor()


        cursor.execute(f"SELECT cs.limite_componente, c.nome AS nome_componente FROM componente_servidor cs JOIN servidor s ON cs.id_servidor = s.id_servidor JOIN componente c ON cs.id_componente = c.id_componente WHERE s.endereco_mac = '{mac}';")

        res = cursor.fetchall()

        limites = []

        for i in res:

            limites.append({

                "componente" : i[1],
                "limite" : i[0]

            })
    finally:
        if db.is_connected():
            cursor.close()
            db.close()


    return next((limite for limite in limites if limite["componente"] == nome), None)["limite"]

def conversao_kb(valor: int):
    return round(valor/(1024), 2)

raw_csv = "raw.csv"
trusted_csv = "trusted.csv"
client_csv = "client.csv"


leitura = pd.read_csv(raw_csv, sep=";")

try:

    client.head_object(Bucket = bucket, Key = "raw/raw.csv")
                
except ClientError as e:

    if e.response['Error']['Code'] == "404":

        client.upload_file(raw_csv,bucket,"raw/raw.csv")

res = client.get_object(Bucket = bucket, Key = "raw/raw.csv")
csvAws = res["Body"].read().decode("utf-8")

with open("csvAws.csv","w",newline= "") as f:

    f.write(csvAws)

with open("csvAws.csv", "a", newline="") as f:

    escritor = csv.writer(f , delimiter=";")
    escritor.writerows(leitura.values)

client.upload_file("csvAws.csv",bucket,"raw/raw.csv")

#os.remove("csvAws.csv")

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
                                   'disk_percent', 'net_kbps_recv', 'net_packets_sent', 'net_packets_recv', 
                                   'net_errin', 'net_errout', 'net_dropin', 'net_dropout', 'usuarios_logados'])
    
leitura.to_csv(trusted_csv, index=False, encoding='utf-8', mode = 'a', header =(not os.path.exists(trusted_csv)))

headersClient = ["idMac","usuarios","timestamp","cpu_percent","cpu_time_user","cpu_ctx_switches","processos_pids_max_cpu","processos_names_max_cpu","processos_cpu_percent_max_cpu","total_processos","virtual_memory_usage","disk_read_kbps","disk_percent","disk_write_kbps","net_kbps_recv","net_packets_recv","net_dropin","net_dropout","usuarios_logados"]

listaMacs = []

for row in leitura:

    print(row)

for index, row in leitura.iterrows():

    if (row["id_mac"] in listaMacs) == False:

        listaMacs.append(row["id_mac"])

print(listaMacs)

dados = []

for mac in listaMacs:

    dados.append({

        "mac" : mac,
        "df" : leitura[leitura["id_mac"] == mac]

        }

    )

print(dados)

linhasClient = []
novasLinhas = []

def categorizar(valor):
    if valor == 0:
        return 'normal'
    else:
        return 'Alerta'


headersClient = ["idMac","usuarios","timestamp","cpu_percent","cpu_time_user","cpu_ctx_switches","processos_pids_max_cpu","processos_names_max_cpu","processos_cpu_percent_max_cpu","total_processos","virtual_memory_usage","disk_read_kbps","disk_percent","disk_write_kbps","net_kbps_recv","net_packets_recv","net_packets_sent","net_dropin","net_dropout","usuarios_logados","virtual_memory_status","cpu_percent_status","disk_percent_status","net_status"]

novasLinhas = []

for dado in dados:

    dado["df"]['virtual_memory_status'] = pd.cut(dado["df"]['virtual_memory_usage'], 
                        bins=[0,pesquisarComponente("ram",dado["mac"]), math.inf], 
                        labels=["Normal","Alerta"])
    
    dado["df"]['cpu_percent_status'] = pd.cut(dado["df"]['cpu_percent'], 
                        bins=[0,pesquisarComponente("CPU",dado["mac"]), math.inf], 
                        labels=["Normal","Alerta"])

    dado["df"]['disk_percent_status'] = pd.cut(dado["df"]['disk_percent'], 
                        bins=[0,pesquisarComponente("memoria",dado["mac"]), math.inf], 
                        labels=["Normal","Alerta"])
    
    dado["df"]['net_status'] = (dado["df"]['net_errin'] + dado["df"]['net_errout'] + dado["df"]['net_dropin'] + dado["df"]['net_dropout']).apply(categorizar)

    print(dado["df"]['disk_percent'])

    dict_virtual_memory_status = dado["df"]['virtual_memory_status'].value_counts().to_dict()
    str_virtual_memory_status = ", ".join([f"{word}: {count}" for word, count in dict_virtual_memory_status.items()])

    dict_cpu_percent_status = dado["df"]['cpu_percent_status'].value_counts().to_dict()
    str_cpu_percent_status = ", ".join([f"{word}: {count}" for word, count in dict_cpu_percent_status.items()])

    dict_disk_percent_status = dado["df"]['disk_percent_status'].value_counts().to_dict()
    str_disk_percent_status = ", ".join([f"{word}: {count}" for word, count in dict_disk_percent_status.items()])
    
    dict_net_status = dado["df"]['net_status'].value_counts().to_dict()
    str_net_status = ", ".join([f"{word}: {count}" for word, count in dict_net_status.items()])

    novasLinhas.append([dado["mac"],
                        dado["df"]['user'].unique().tolist(),
                        datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                        dado["df"]["cpu_percent"].max(),
                        dado["df"]["cpu_time_user"].sum(),
                        dado["df"]["cpu_ctx_switches"].sum(),
                        dado["df"]["processo_pid_max_cpu"].unique().tolist(),
                        dado["df"]["processo_name_max_cpu"].unique().tolist(),
                        dado["df"].groupby("processo_name_max_cpu")["processo_cpu_percent_max_cpu"].max().to_dict(),
                        str(dado["df"]["total_processos"].sum()),
                        str(dado["df"]["virtual_memory_usage"].max()),
                        str(dado["df"]["disk_read_kbps"].max()),
                        str(dado["df"]['disk_percent'].max()),
                        str(dado["df"]["disk_write_kbps"].max()),
                        str(dado["df"]["net_kbps_recv"].max()),
                        dado["df"]["net_packets_sent"].max(),
                         dado["df"]["net_packets_sent"].max(),
                        dado["df"]["net_dropin"].sum(),
                        dado["df"]["net_dropout"].sum(),
                        dado["df"]["usuarios_logados"].sum(),
                        str_virtual_memory_status,
                        str_cpu_percent_status,
                        str_disk_percent_status,
                        str_net_status])

clientDf = pd.DataFrame(novasLinhas, columns=headersClient)

clientDf.to_csv(client_csv, mode="a", header=not os.path.exists(client_csv))

os.remove(raw_csv)