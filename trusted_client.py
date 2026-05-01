from dotenv import load_dotenv
import pandas as pd
import csv
import os
import math
from io import StringIO
import mysql.connector
from datetime import datetime
import boto3
from botocore.exceptions import ClientError
import numpy as np

load_dotenv()

client = boto3.client(

    "s3",
    aws_access_key_id=os.getenv("aws_access_key_id"),
    aws_secret_access_key=os.getenv("aws_secret_access_key"),
    aws_session_token=os.getenv("aws_session_token")
)

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


    print (limites)
    print(next((limite for limite in limites if limite["componente"] == nome), None)["limite"])

    return next((limite for limite in limites if limite["componente"] == nome), None)["limite"]

def conversao_kb(valor: int):
    return round(valor/(1024), 2)

raw_csv = "raw.csv"
trusted_csv = "trusted.csv"
client_csv = "client.csv"

paginator = client.get_paginator('list_objects_v2')
lista_raws = []


for page in paginator.paginate(Bucket=bucket, Prefix="raw/"):
    for obj in page["Contents"]:
        chave = obj["Key"]
        response = client.get_object(Bucket=bucket, Key=chave)
        
        # READ AND DECODE HERE so it's stored in the dictionary
        content_string = response['Body'].read().decode('utf-8')
        
        lista_raws.append({
            "nome": obj["Key"][4:21],
            "conteudo_str": content_string, # Save the actual string
            "LastModified": response["LastModified"] # Save this for sorting
        })
lista_raws = sorted(lista_raws, key=lambda x: x["LastModified"], reverse=True)



raws = []
ultimos_raws = []

for obj in lista_raws:

    if not obj["nome"] in raws:

        ultimos_raws.append(obj)
        raws.append(obj["nome"])



dataframes_raw = []

leitura = pd.DataFrame()

for raw in ultimos_raws:
    csv_data = raw['conteudo_str']
    if csv_data.strip():
        df = pd.read_csv(StringIO(csv_data), sep=";")
        dataframes_raw.append(df)

if dataframes_raw:
    leitura = pd.concat(dataframes_raw, ignore_index=True)
print(dataframes_raw)



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
    
try:

    client.head_object(Bucket = bucket, Key = "trusted/trusted.csv")

    trusted = client.get_object(Bucket = bucket, Key = "trusted/trusted.csv")

    with open(trusted_csv,"w",newline="") as f:

        f.write(trusted["Body"].read().decode("utf-8"))

    leitura.to_csv(trusted_csv, index=False, encoding='utf-8', mode = 'a', header =(not os.path.exists(trusted_csv)))

    client.upload_file(trusted_csv,bucket,"trusted/trusted.csv")

    os.remove(trusted_csv)

except ClientError as e:
    
    if e.response['Error']['Code'] == "404":

        leitura.to_csv(trusted_csv, index=False, encoding='utf-8', mode = 'a', header =(not os.path.exists(trusted_csv)))

        client.upload_file(trusted_csv,bucket,"trusted/trusted.csv")

        os.remove(trusted_csv)

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


headersClient = ["idMac","usuarios","timestamp","cpu_percent","cpu_time_user","cpu_ctx_switches","processos_pids_max_cpu","processos_names_max_cpu","processos_cpu_percent_max_cpu","total_processos","virtual_memory_usage","disk_read_kbps","disk_percent","disk_write_kbps","net_kbps_recv","net_packets_recv","net_packets_sent","net_dropin","net_dropout","usuarios_logados","virtual_memory_status","cpu_percent_status","disk_percent_status","net_errors"]

novasLinhas = []

for dado in dados:
    
    dado["df"]["virtual_memory_status"] = np.where(dado["df"]['virtual_memory_usage'] >= pesquisarComponente("Memória Usada (%)",dado["mac"]),"Normal","Alerta" )

    dado["df"]["cpu_percent_status"] = np.where(dado["df"]['cpu_percent'] >= pesquisarComponente("Uso de CPU (%)",dado["mac"]),"Normal","Alerta" )

    dado["df"]["disk_percent_status"] = np.where(dado["df"]["disk_percent"] >= pesquisarComponente("Memória Usada (%)",dado["mac"]),"Normal","Alerta" )
    
    #if dado["df"]['virtual_memory_usage'] < pesquisarComponente("Memória Usada (%)",dado["mac"]):
    #    dado["df"]["virtual_memory_status"] = "Normal"
    #else:
    #    dado["df"]["virtual_memory_status"] = "Alerta"

    #if dado["df"]['cpu_percent'] < pesquisarComponente("Uso de CPU (%)",dado["mac"]):
    #    dado["df"]["cpu_percent_status"] = "Normal"
    #else:
    #    dado["df"]["cpu_percent_status"] = "Alerta"

    #if dado["df"]['disk_percent'] < pesquisarComponente("Uso de Disco (%)",dado["mac"]):
    #    dado["df"]["disk_percent_status"] = "Normal"
    #else:
    #    dado["df"]["disk_percent_status"] = "Alerta"
    
    dado["df"]['net_errors'] = (dado["df"]['net_errin'] + dado["df"]['net_errout'] + dado["df"]['net_dropin'] + dado["df"]['net_dropout']).apply(categorizar)

    print(dado["df"]['disk_percent'])

    dict_virtual_memory_status = dado["df"]['virtual_memory_status'].value_counts().to_dict()
    str_virtual_memory_status = ", ".join([f"{word}: {count}" for word, count in dict_virtual_memory_status.items()])

    dict_cpu_percent_status = dado["df"]['cpu_percent_status'].value_counts().to_dict()
    str_cpu_percent_status = ", ".join([f"{word}: {count}" for word, count in dict_cpu_percent_status.items()])

    dict_disk_percent_status = dado["df"]['disk_percent_status'].value_counts().to_dict()
    str_disk_percent_status = ", ".join([f"{word}: {count}" for word, count in dict_disk_percent_status.items()])
    
    dict_net_errors = dado["df"]['net_errors'].value_counts().to_dict()
    str_net_errors = ", ".join([f"{word}: {count}" for word, count in dict_net_errors.items()])

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
                        str_net_errors])

clientDf = pd.DataFrame(novasLinhas, columns=headersClient)
clientDf.to_csv(client_csv, mode="a", header=not os.path.exists(client_csv), index = False)

try:

    client.head_object(Bucket = bucket, Key = "client/client.csv")

    clientt = client.get_object(Bucket = bucket, Key = "client/client.csv")

    with open(client_csv,"w",newline="") as f:

        f.write(clientt["Body"].read().decode("utf-8"))

    clientDf.to_csv(client_csv, mode="a", header=not os.path.exists(client_csv), index = False)

    client.upload_file(client_csv,bucket,"client/client.csv")

    os.remove(client_csv)

except ClientError as e:
    
    if e.response['Error']['Code'] == "404":

        clientDf.to_csv(client_csv, mode="a", header=not os.path.exists(client_csv), index = False)

        client.upload_file(client_csv,bucket,"client/client.csv")

        os.remove(client_csv)
