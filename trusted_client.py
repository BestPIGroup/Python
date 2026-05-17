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

client = boto3.client("s3")

bucket = os.getenv("bucket")

def lambda_handler(event, context):

    def pesquisarComponente(nome,mac):

        db = None
        cursor = None

        try:

            db = mysql.connector.connect(
            host= os.getenv("host"),
            user= os.getenv("user"),
            password= os.getenv("password"),
            database= os.getenv("database")
            )

            cursor = db.cursor()

            query = """
            SELECT 
                cs.limite_componente,
                c.nome AS nome_componente
            FROM componente_servidor cs
            JOIN servidor s 
                    ON cs.id_servidor = s.id_servidor
            JOIN componente c 
                    ON cs.id_componente = c.id_componente
            WHERE s.endereco_mac = %s;
            """

            cursor.execute(query, (mac,))

            res = cursor.fetchall()

            limites = []

            for i in res:

                limites.append({

                    "componente" : i[1],
                    "limite" : i[0]

                })

        except Exception as e:
        
            print("Erro ao conectar no banco:", e)
            return 0
        
        finally:

            if cursor is not None:
                cursor.close()

            if db is not None and db.is_connected():
                db.close()


        # print (limites)
        # print(next((limite for limite in limites if limite["componente"] == nome), None)["limite"])

        # return next((limite for limite in limites if limite["componente"] == nome), None)["limite"]
    
        resultado = next(
            (limite for limite in limites if limite["componente"] == nome),
            None
        )

        print("Resultado encontrado:", resultado)

        if resultado is None:

            print(f"Componente '{nome}' não encontrado para MAC {mac}")

            return 0

        return resultado["limite"]

    def conversao_kb(valor: int):
        return round(valor/(1024), 2)

    paginator = client.get_paginator('list_objects_v2')
    lista_raws = []


    for page in paginator.paginate(Bucket=bucket, Prefix="raw/"):

        if "Contents" not in page:
            continue

        for obj in page["Contents"]:

            chave = obj["Key"]

            if chave.endswith("/"):
                continue

            response = client.get_object(Bucket=bucket, Key=chave)
            
            content_string = response['Body'].read().decode('utf-8')
            
            lista_raws.append({
                "nome": obj["Key"][4:21],
                "conteudo_str": content_string,
                "LastModified": obj["LastModified"]
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

    leitura['virtual_memory_usage'] = 100*((leitura['virtual_memory_total'] - leitura['virtual_memory_available'])/leitura['virtual_memory_total'])

    leitura.drop(columns=['virtual_memory_total', 'virtual_memory_available'], inplace=True)
    
    leitura = leitura.reindex(columns=['user', 'id_mac', 'timestamp', 'cpu_percent', 'cpu_time_user', 'cpu_ctx_switches', 
                                   'top_3_processos_cpu', 'top_3_processos_disco', 'total_processos', 'virtual_memory_usage', 
                                   'disk_read_kbps', 'disk_write_kbps', 'disk_percent', 'net_kbps_recv', 'net_packets_sent', 
                                   'net_packets_recv', 'net_errin', 'net_errout', 'net_dropin', 'net_dropout', 'usuarios_logados'])
    

    leitura.rename(columns={'disk_read_bytes' : 'disk_read_kbps', 'disk_write_bytes' : 'disk_write_kbps','net_bytes_sent' : 'net_kbps_sent', 'net_bytes_recv' : 'net_kbps_recv'}, inplace=True)

    leitura['disk_read_kbps']=conversao_kb(leitura['disk_read_bytes']/5)
    leitura['disk_write_kbps']=conversao_kb(leitura['disk_write_bytes']/5)
    leitura['net_kbps_sent']=conversao_kb(leitura['net_bytes_sent']/5)
    leitura['net_kbps_recv']=conversao_kb(leitura['net_bytes_recv']/5)

    leitura['timestamp'] = pd.to_datetime(leitura['timestamp'], format='%Y-%m-%d %H:%M:%S')
    leitura['timestamp'] = leitura['timestamp'].dt.strftime('%d/%m/%Y %H:%M:%S')

    trusted_csv_buffer = StringIO()

    try:

        trusted = client.get_object(Bucket = bucket, Key = "trusted/trusted.csv")

        trusted_existente = pd.read_csv(
            StringIO(trusted["Body"].read().decode("utf-8"))
        )

        trusted_final = pd.concat([trusted_existente, leitura], ignore_index=True)

        trusted_final.to_csv(trusted_csv_buffer, index=False)

        client.put_object(
            Bucket=bucket,
            Key="trusted/trusted.csv",
            Body=trusted_csv_buffer.getvalue()
        )

    except ClientError as e:
        
        if e.response['Error']['Code'] == "NoSuchKey":

            leitura.to_csv(trusted_csv_buffer, index=False)

            client.put_object(
                Bucket=bucket,
                Key="trusted/trusted.csv",
                Body=trusted_csv_buffer.getvalue()
            )

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


    headersClient = ["idMac","usuarios","timestamp","cpu_percent","cpu_time_user","cpu_ctx_switches","top_3_processos_cpu","top_3_processos_disco","total_processos","virtual_memory_usage","disk_read_kbps","disk_percent","disk_write_kbps","net_kbps_recv","net_packets_recv","net_packets_sent","net_dropin","net_dropout","usuarios_logados","virtual_memory_status","cpu_percent_status","disk_percent_status","net_errors","total_arquivos_abertos"]

    novasLinhas = []

    for dado in dados:
        
        dado["df"]["virtual_memory_status"] = np.where(dado["df"]['virtual_memory_usage'] < pesquisarComponente("Memória Usada (%)",dado["mac"]),"Normal","Alerta" )

        dado["df"]["cpu_percent_status"] = np.where(dado["df"]['cpu_percent'] < pesquisarComponente("Uso de CPU (%)",dado["mac"]),"Normal","Alerta" )

        dado["df"]["disk_percent_status"] = np.where(dado["df"]["disk_percent"] < pesquisarComponente("Uso de Disco (%)",dado["mac"]),"Normal","Alerta" )
        
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
                        dado["df"]["top_3_processos_cpu"].str.cat(", "),
                        dado["df"]["top_3_processos_disco"].str.cat(", "),
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
                        dado["df"]["arquivos_abertos"].sum(),
                        str_virtual_memory_status,
                        str_cpu_percent_status,
                        str_disk_percent_status,
                        str_net_errors])

    clientDf = pd.DataFrame(novasLinhas, columns=headersClient)

    client_csv_buffer = StringIO()

    try:

        clientt = client.get_object(Bucket = bucket, Key = "client/client.csv")

        client_existente = pd.read_csv(
            StringIO(clientt["Body"].read().decode("utf-8"))
            ,sep=";"
        )

        client_final = pd.concat([client_existente, clientDf], ignore_index=True)   

        client_final.to_csv(client_csv_buffer, index=False, sep=";")

        client.put_object(
            Bucket=bucket,
            Key="client/client.csv",
            Body=client_csv_buffer.getvalue()
        )

    except ClientError as e:
        
        if e.response['Error']['Code'] == "NoSuchKey":

            clientDf.to_csv(client_csv_buffer, index=False,sep=";")

            client.put_object(
                Bucket=bucket,
                Key="client/client.csv",
                Body=client_csv_buffer.getvalue()
            )

    return {
        "statusCode": 200,
        "body": "ETL executado com sucesso"
    }