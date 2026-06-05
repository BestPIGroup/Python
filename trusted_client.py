import pandas as pd
import csv
import os
import math
from io import StringIO
import mysql.connector
from datetime import datetime, timedelta, timezone
import boto3
from botocore.exceptions import ClientError
import numpy as np
import json

cliente_s3 = boto3.client("s3")

bucket = os.getenv("bucket")

def lambda_handler(event, context):

    def pesquisarComponente(nome, mac):

        db = None
        cursor = None

        try:
            db = mysql.connector.connect(
                host=os.getenv("host"),
                user=os.getenv("user"),
                password=os.getenv("password"),
                database=os.getenv("database")
            )

            cursor = db.cursor()

            cursor.execute(f"""
                SELECT cs.limite_componente, c.nome AS nome_componente 
                FROM componente_servidor cs 
                JOIN servidor s ON cs.id_servidor = s.id_servidor 
                JOIN componente c ON cs.id_componente = c.id_componente 
                WHERE s.endereco_mac = '{mac}';
            """)

            res = cursor.fetchall()

            limites = []

            for i in res:
                limites.append({
                    "componente": i[1],
                    "limite": i[0]
                })

        finally:
            if db is not None and db.is_connected():
                cursor.close()
                db.close()

        print(limites)

        resultado = next((limite for limite in limites if limite["componente"] == nome), None)

        if resultado is None:
            return None

        print(resultado["limite"])

        return resultado["limite"]

    def conversao_kb(valor):
        return round(valor / (1024), 2)
    
    def conversao_mb(valor):
        return round(valor / (1024**2), 2)

    paginador = cliente_s3.get_paginator('list_objects_v2')
    lista_raws = []

    for pagina in paginador.paginate(Bucket=bucket, Prefix="raw/"):

        if "Contents" not in pagina:
            continue

        for obj in pagina["Contents"]:

            chave = obj["Key"]

            if chave.endswith("/"):
                continue

            resposta = cliente_s3.get_object(Bucket=bucket, Key=chave)

            conteudo_string = resposta['Body'].read().decode('utf-8')

            lista_raws.append({
                "nome": obj["Key"][4:21],
                "conteudo_str": conteudo_string,
                "LastModified": obj["LastModified"]
            })

    lista_raws = sorted(lista_raws, key=lambda x: x["LastModified"], reverse=True)

    raws = []
    ultimos_raws = []

    for obj in lista_raws:

        if obj["nome"] not in raws:
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

    leitura['virtual_memory_usage'] = 100 * ((leitura['virtual_memory_total'] - leitura['virtual_memory_available']) / leitura['virtual_memory_total'])

    leitura.drop(columns=['virtual_memory_total', 'virtual_memory_available'], inplace=True)

    leitura = leitura.reindex(columns=[
        'user', 'id_mac', 'timestamp', 'cpu_percent', 'cpu_time_user', 'cpu_ctx_switches',
        'top_3_processos_cpu', 'top_3_processos_disco', 'total_processos', 'virtual_memory_usage',
        'disk_read_bytes', 'disk_write_bytes', 'disk_percent', 'net_bytes_recv', 'net_bytes_sent',
        'net_packets_sent', 'net_packets_recv', 'net_errin', 'net_errout', 'net_dropin',
        'net_dropout', 'usuarios_logados', 'arquivos_abertos'
    ])

    leitura.rename(columns={
        'disk_read_bytes': 'disk_read_mbps',
        'disk_write_bytes': 'disk_write_mbps',
        'net_bytes_sent': 'net_kbps_sent',
        'net_bytes_recv': 'net_kbps_recv'
    }, inplace=True)

    leitura['disk_read_mbps'] = conversao_mb(leitura['disk_read_mbps'] / 5)
    leitura['disk_write_mbps'] = conversao_mb(leitura['disk_write_mbps'] / 5)
    leitura['net_kbps_sent'] = conversao_kb(leitura['net_kbps_sent'] / 5)
    leitura['net_kbps_recv'] = conversao_kb(leitura['net_kbps_recv'] / 5)

    leitura['timestamp'] = pd.to_datetime(leitura['timestamp'], format='%Y-%m-%d %H:%M:%S')
    leitura['timestamp'] = leitura['timestamp'].dt.strftime('%d/%m/%Y %H:%M:%S')

    buffer_csv_trusted = StringIO()

    try:
        trusted = cliente_s3.get_object(Bucket=bucket, Key="trusted/trusted.csv")

        trusted_existente = pd.read_csv(
            StringIO(trusted["Body"].read().decode("utf-8")),
            sep=";"
        )

        trusted_final = pd.concat([trusted_existente, leitura], ignore_index=True)

        trusted_final.to_csv(buffer_csv_trusted, index=False, sep=";")

        cliente_s3.put_object(
            Bucket=bucket,
            Key="trusted/trusted.csv",
            Body=buffer_csv_trusted.getvalue()
        )

    except ClientError as e:

        if e.response['Error']['Code'] == "NoSuchKey":

            leitura.to_csv(buffer_csv_trusted, index=False, sep=";")

            cliente_s3.put_object(
                Bucket=bucket,
                Key="trusted/trusted.csv",
                Body=buffer_csv_trusted.getvalue()
            )

    listaMacs = []

    for index, row in leitura.iterrows():

        if row["id_mac"] not in listaMacs:
            listaMacs.append(row["id_mac"])

    print(listaMacs)

    dados = []

    for mac in listaMacs:
        dados.append({
            "mac": mac,
            "df": leitura[leitura["id_mac"] == mac]
        })

    print(dados)

    novasLinhas = []
    novasLinhasAlertas = []

    linhaNomeArquivo = {}
    linhaNomeArquivoDefinida = False

    def categorizar(valor):
        if valor == 0:
            return 'normal'
        else:
            return 'Alerta'

    headersClient = [
        "idMac", "usuarios", "timestamp", "cpu_percent", "cpu_time_user", "cpu_ctx_switches",
        "top_3_processos_cpu", "top_3_processos_disco", "total_processos", "virtual_memory_usage",
        "disk_read_mbps", "disk_percent", "disk_write_mbps", "net_kbps_sent", "net_kbps_recv",
        "net_packets_sent", "net_packets_recv", "net_dropin", "net_dropout", "usuarios_logados",
        "virtual_memory_status", "cpu_percent_status", "disk_percent_status", "net_errors",
        "total_arquivos_abertos", "mediana_net_sent", "mediana_net_recv"
    ]

    for dado in dados:

        if linhaNomeArquivoDefinida == False:
            linhaNomeArquivo = dado
            linhaNomeArquivoDefinida = True

        alertaRAM = False
        alertaCPU = False
        alertaDisco = False
        alertaProcessos = False
        alertaRede = False
        alertaCtxSwt = False
        mensagensAlerta = []

        moda_sent = dado["df"]["net_kbps_sent"].mode()
        moda_recv = dado["df"]["net_kbps_recv"].mode()

        moda_sent = moda_sent.iloc[0] if not moda_sent.empty else 0
        moda_recv = moda_recv.iloc[0] if not moda_recv.empty else 0

        dado["df"] = dado["df"].copy()

        limiteRAM = pesquisarComponente("Memoria Usada (%)", dado["mac"])
        if limiteRAM is not None:
            dado["df"]["virtual_memory_status"] = np.where(
                dado["df"]['virtual_memory_usage'] >= limiteRAM,
                "Alerta", "Normal"
            )
            if (dado["df"]["virtual_memory_status"] == "Alerta").any():
                alertaRAM = True
                mensagensAlerta.append({"RAM": "Alto uso da RAM"})
        else:
            dado["df"]["virtual_memory_status"] = "Normal"

        limiteCPU = pesquisarComponente("Uso de CPU (%)", dado["mac"])
        if limiteCPU is not None:
            dado["df"]["cpu_percent_status"] = np.where(
                dado["df"]['cpu_percent'] >= limiteCPU,
                "Alerta", "Normal"
            )
            if (dado["df"]["cpu_percent_status"] == "Alerta").any():
                alertaCPU = True
                mensagensAlerta.append({"CPU": "Alto uso da CPU"})
        else:
            dado["df"]["cpu_percent_status"] = "Normal"

        limiteCtxSwt = pesquisarComponente("Trocas de contexto", dado["mac"])
        if limiteCtxSwt is not None:
            dado["df"]["cpu_ctx_switches_status"] = np.where(
                dado["df"]["cpu_ctx_switches"] >= limiteCtxSwt,
                "Alerta", "Normal"
            )
            if (dado["df"]["cpu_ctx_switches_status"] == "Alerta").any():
                alertaCtxSwt = True
                mensagensAlerta.append({"CPU": "Troca alta de contexto na CPU"})
        else:
            dado["df"]["cpu_ctx_switches_status"] = "Normal"

        limiteDisco = pesquisarComponente("Uso de Disco (%)", dado["mac"])
        if limiteDisco is not None:
            dado["df"]["disk_percent_status"] = np.where(
                dado["df"]["disk_percent"] >= limiteDisco,
                "Alerta", "Normal"
            )
            if (dado["df"]["disk_percent_status"] == "Alerta").any():
                alertaDisco = True
                mensagensAlerta.append({"DISCO": "Disco com capacidade exaurida"})
        else:
            dado["df"]["disk_percent_status"] = "Normal"

        dado["df"]['net_errors'] = (
            dado["df"]['net_errin'] +
            dado["df"]['net_errout'] +
            dado["df"]['net_dropin'] +
            dado["df"]['net_dropout']
        ).apply(categorizar)

        if (dado["df"]['net_errors'] == "Alerta").any():
            alertaRede = True
            mensagensAlerta.append({"REDE": "Request denied por motivo desconhecido"})

        ## ALERTAS DE CYBERSEGURANÇA
        if alertaCPU and alertaProcessos and alertaCtxSwt:
            mensagensAlerta.append({"Malware": "Possibilidade de ataque Malware"})

        if alertaCPU and alertaDisco:
            mensagensAlerta.append({"Ransomware": "Possibilidade de ataque Ransomware"})

        ## ALERTAS DE ATAQUE DDOS
        if (dado["df"]["net_kbps_sent"].max() - dado["df"]["net_kbps_recv"].max()) > (((dado["df"]["net_kbps_sent"].max() + dado["df"]["net_kbps_recv"].max())/2)*.5 ) or (dado["df"]["net_kbps_recv"].max() - dado["df"]["net_packets_sent"].sum()) > (((dado["df"]["net_kbps_recv"].max() + dado["df"]["net_packets_sent"].sum())/2)*.5):
            mensagensAlerta.append({"DDOS": "Possibilidade de ataque DDOS"})


        if alertaCPU or alertaDisco or alertaRAM or alertaRede or alertaProcessos or alertaCtxSwt:
            novasLinhasAlertas.append([
                dado["df"]["timestamp"].iloc[-1],
                dado["mac"],
                mensagensAlerta
            ])

        print(dado["df"]['disk_percent'])

        dict_virtual_memory_status = dado["df"]['virtual_memory_status'].value_counts().to_dict()
        str_virtual_memory_status = ", ".join([f"{palavra}: {contagem}" for palavra, contagem in dict_virtual_memory_status.items()])

        dict_cpu_percent_status = dado["df"]['cpu_percent_status'].value_counts().to_dict()
        str_cpu_percent_status = ", ".join([f"{palavra}: {contagem}" for palavra, contagem in dict_cpu_percent_status.items()])

        dict_disk_percent_status = dado["df"]['disk_percent_status'].value_counts().to_dict()
        str_disk_percent_status = ", ".join([f"{palavra}: {contagem}" for palavra, contagem in dict_disk_percent_status.items()])

        dict_net_errors = dado["df"]['net_errors'].value_counts().to_dict()
        str_net_errors = ", ".join([f"{palavra}: {contagem}" for palavra, contagem in dict_net_errors.items()])

        novasLinhas.append([
            dado["mac"],
            dado["df"]['user'].unique().tolist(),
            datetime.now(timezone(timedelta(hours=-3))).strftime('%d/%m/%Y %H:%M:%S'),
            dado["df"]["cpu_percent"].max(),
            dado["df"]["cpu_time_user"].sum(),
            dado["df"]["cpu_ctx_switches"].sum(),
            dado["df"]["top_3_processos_cpu"].str.cat(sep=", "),
            dado["df"]["top_3_processos_disco"].str.cat(sep=", "),
            str(dado["df"]["total_processos"].sum()),
            str(dado["df"]["virtual_memory_usage"].max()),
            str(dado["df"]["disk_read_mbps"].max()),
            str(dado["df"]['disk_percent'].max()),
            str(dado["df"]["disk_write_mbps"].max()),
            str(dado["df"]["net_kbps_sent"].max()),
            str(dado["df"]["net_kbps_recv"].max()),
            dado["df"]["net_packets_sent"].sum(),
            dado["df"]["net_packets_recv"].sum(),
            dado["df"]["net_dropin"].sum(),
            dado["df"]["net_dropout"].sum(),
            dado["df"]["usuarios_logados"].sum(),
            str_virtual_memory_status,
            str_cpu_percent_status,
            str_disk_percent_status,
            str_net_errors,
            dado["df"]["arquivos_abertos"].sum(),
            moda_sent,
            moda_recv
        ])

    data_hoje = datetime.now(timezone(timedelta(hours=-3))).strftime("%d-%m-%y")
    aws_alerta_key = f"logAlertas/{data_hoje}_{linhaNomeArquivo['mac']}.csv"

    try:
        alertaGetObj = cliente_s3.get_object(Bucket=bucket, Key=aws_alerta_key)
        alerta_existente = pd.read_csv(
            StringIO(alertaGetObj["Body"].read().decode("utf-8")),
            sep=";"
        )
        alerta_novo = pd.concat(
            [alerta_existente, pd.DataFrame(novasLinhasAlertas, columns=alerta_existente.columns)],
            ignore_index=True
        )
    except ClientError as e:
        if e.response['Error']['Code'] == "NoSuchKey":
            alerta_novo = pd.DataFrame(novasLinhasAlertas, columns=["Timestamp", "MacAdress", "MensagensAlerta"])
        else:
            raise

    try:
        buffer_csv_alerta = StringIO()
        alerta_novo.to_csv(buffer_csv_alerta, index=False, sep=";", encoding="utf-8")

        cliente_s3.put_object(
            Bucket=bucket,
            Key=aws_alerta_key,
            Body=buffer_csv_alerta.getvalue()
        )
    except Exception as e:
        print(f"Não foi possível acessar o S3: {e}")

    alertasDf = pd.DataFrame(novasLinhasAlertas, columns=["Timestamp", "MacAdress", "MensagensAlerta"])

    clientDf = pd.DataFrame(novasLinhas, columns=headersClient)

    buffer_csv_client = StringIO()

    try:
        clientt = cliente_s3.get_object(Bucket=bucket, Key="client/client.csv")

        client_existente = pd.read_csv(
            StringIO(clientt["Body"].read().decode("utf-8")),
            sep=";"
        )

        client_final = pd.concat([client_existente, clientDf], ignore_index=True)

        client_final.to_csv(buffer_csv_client, index=False, sep=";")

        cliente_s3.put_object(
            Bucket=bucket,
            Key="client/client.csv",
            Body=buffer_csv_client.getvalue()
        )

    except ClientError as e:

        if e.response['Error']['Code'] == "NoSuchKey":

            clientDf.to_csv(buffer_csv_client, index=False, sep=";")

            cliente_s3.put_object(
                Bucket=bucket,
                Key="client/client.csv",
                Body=buffer_csv_client.getvalue()
            )

    return {
        "statusCode": 200,
        "body": "ETL executado com sucesso"
    }
