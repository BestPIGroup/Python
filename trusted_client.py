import pandas as pd
import csv
import os
import math
import ast  # adicionado para interpretar as listas
from io import StringIO
import mysql.connector
from datetime import datetime, timedelta, timezone
import boto3
from botocore.exceptions import ClientError
import numpy as np
import json
import random

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

    def simular_ransomware(df_mac):
        df_sim = df_mac.copy()
        chance = random.random()

        if chance < 0.7:
            fator_cpu = random.uniform(60.0, 95.0)
            fator_ram = random.uniform(1.1, 1.5)
            fator_disco = random.uniform(4.0, 8.0)

            df_sim['cpu_percent'] = (df_sim['cpu_percent'] + fator_cpu).clip(upper=100)
            df_sim['virtual_memory_usage'] = (df_sim['virtual_memory_usage'] * fator_ram).clip(upper=98)
            df_sim['disk_write_kbps'] = df_sim['disk_write_kbps'] * fator_disco
            df_sim['disk_read_kbps'] = df_sim['disk_read_kbps'] * fator_disco

            escrita_simulada = int(df_sim['disk_write_kbps'].iloc[-1] * 1024)

            handles1 = random.randint(800, 1500)
            handles2 = random.randint(400, 800)
            handles3 = random.randint(200, 400)

            processo_falso = f"[[9999, 'encrypt.exe', {escrita_simulada}, {handles1}], [9998, 'crypt_worker.exe', {int(escrita_simulada * 0.6)}, {handles2}], [9997, 'file_scan.exe', {int(escrita_simulada * 0.3)}, {handles3}]]"
            df_sim['top_3_processos_disco'] = processo_falso

        return df_sim

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
        'net_dropout', 'usuarios_logados'
    ])

    leitura.rename(columns={
        'disk_read_bytes': 'disk_read_kbps',
        'disk_write_bytes': 'disk_write_kbps',
        'net_bytes_sent': 'net_kbps_sent',
        'net_bytes_recv': 'net_kbps_recv'
    }, inplace=True)

    leitura['disk_read_kbps'] = conversao_kb(leitura['disk_read_kbps'] / 5)
    leitura['disk_write_kbps'] = conversao_kb(leitura['disk_write_kbps'] / 5)
    leitura['net_kbps_sent'] = conversao_kb(leitura['net_kbps_sent'] / 5)
    leitura['net_kbps_recv'] = conversao_kb(leitura['net_kbps_recv'] / 5)

    leitura['timestamp'] = pd.to_datetime(leitura['timestamp'], format='%Y-%m-%d %H:%M:%S')
    leitura['timestamp'] = leitura['timestamp'].dt.strftime('%d/%m/%Y %H:%M:%S')

    listaMacs = []

    for index, row in leitura.iterrows():
        if row["id_mac"] not in listaMacs:
            listaMacs.append(row["id_mac"])

    print(listaMacs)

    for mac in listaMacs:
        df_mac = leitura[leitura["id_mac"] == mac].copy()
        df_mac = simular_ransomware(df_mac)
        colunas_sim = ["cpu_percent", "virtual_memory_usage", "disk_write_kbps", "disk_read_kbps", "top_3_processos_disco"]
        leitura.loc[leitura["id_mac"] == mac, colunas_sim] = df_mac[colunas_sim].values

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

            trusted_final = leitura.copy()

            leitura.to_csv(buffer_csv_trusted, index=False, sep=";")

            cliente_s3.put_object(
                Bucket=bucket,
                Key="trusted/trusted.csv",
                Body=buffer_csv_trusted.getvalue()
            )

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
        
    def top_processos_max_por_mac(df, coluna):
        todos = []
        for valor in df[coluna]:
            if pd.isna(valor) or not isinstance(valor, str):
                continue
            try:
                processos = ast.literal_eval(valor)
                todos.extend(processos)
            except (ValueError, SyntaxError):
                continue

        if not todos:
            return "[]"

        max_por_pid = {}
        for pid, nome, uso in todos:
            chave = (pid, nome)
            if chave not in max_por_pid or uso > max_por_pid[chave]:
                max_por_pid[chave] = uso

        top3 = sorted(
            [[pid, nome, uso] for (pid, nome), uso in max_por_pid.items()],
            key=lambda x: x[2], reverse=True
        )[:3]

        return str(top3)
    

    def top_processos_max_por_mac_disco(df, coluna):

        todos = []

        for valor in df[coluna]:
            if pd.isna(valor) or not isinstance(valor, str):
                continue
            try:
                processos = ast.literal_eval(valor)
                todos.extend(processos)
            except (ValueError, SyntaxError):
                continue

        if not todos:
            return "[]"

        max_por_pid = {}

        for pid, nome, uso, handles in todos:
            chave = (pid, nome)

            if chave not in max_por_pid or uso > max_por_pid[chave][0]:
                max_por_pid[chave] = (uso, handles)

        top3 = sorted(
            [[pid, nome, uso, handles] for (pid, nome), (uso, handles) in max_por_pid.items()],
            key=lambda x: x[2],
            reverse=True
        )[:3]

        return str(top3)
            

    def calcularScore(linha, limite_cpu, limite_ram, limite_escrita_kb, limite_leitura_kb):

        score = 0

        if limite_cpu and linha["cpu_percent"] > limite_cpu:
            score += 25

        if limite_ram and linha["virtual_memory_usage"] > limite_ram:
            score += 25

        if limite_escrita_kb and linha["disk_write_kbps"] > limite_escrita_kb:
            score += 25

        if limite_leitura_kb and linha["disk_read_kbps"] > limite_leitura_kb:
            score += 25

        if score >= 75:
            nivel = "ALTO"
        elif score >= 25:
            nivel = "MEDIO"
        else:
            nivel = "BAIXO"

        return score, nivel

    headersClient = [
        "idMac", "usuarios", "timestamp", "cpu_percent", "cpu_time_user", "cpu_ctx_switches",
        "top_3_processos_cpu", "top_3_processos_disco", "total_processos", "virtual_memory_usage",
        "disk_read_kbps", "disk_percent", "disk_write_kbps", "net_kbps_sent", "net_kbps_recv",
        "net_packets_sent", "net_packets_recv", "net_dropin", "net_dropout", "usuarios_logados",
        "virtual_memory_status", "cpu_percent_status", "disk_percent_status", "net_errors",
        "mediana_vel_sent", "mediana_vel_recv"
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
        alertaEscrita = False
        alertaLeitura = False
        mensagensAlerta = []

        moda_sent = dado["df"]["net_kbps_sent"].median()
        moda_recv = dado["df"]["net_kbps_recv"].median()

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

        limiteEscrita = pesquisarComponente("Escrita em Disco (KB/s)", dado["mac"])
        if limiteEscrita is not None:
            dado["df"]["disk_write_status"] = np.where(
                dado["df"]["disk_write_kbps"] >= limiteEscrita,
                "Alerta", "Normal"
            )
            alertaEscrita = (dado["df"]["disk_write_status"] == "Alerta").any()
        else:
            dado["df"]["disk_write_status"] = "Normal"
            alertaEscrita = False

        limiteLeitura = pesquisarComponente("Leitura em Disco (KB/s)", dado["mac"])
        if limiteLeitura is not None:
            dado["df"]["disk_read_status"] = np.where(
                dado["df"]["disk_read_kbps"] >= limiteLeitura,
                "Alerta", "Normal"
            )
            alertaLeitura = (dado["df"]["disk_read_status"] == "Alerta").any()
        else:
            dado["df"]["disk_read_status"] = "Normal"
            alertaLeitura = False

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

        if alertaCPU and (alertaEscrita or alertaLeitura):
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

        top_cpu_str = top_processos_max_por_mac(dado["df"], 'top_3_processos_cpu')
        top_disco_str = top_processos_max_por_mac_disco(dado["df"], 'top_3_processos_disco')

        novasLinhas.append([
            dado["mac"],
            dado["df"]['user'].unique().tolist(),
            datetime.now(timezone(timedelta(hours=-3))).strftime('%d/%m/%Y %H:%M:%S'),
            dado["df"]["cpu_percent"].max(),
            dado["df"]["cpu_time_user"].sum(),
            dado["df"]["cpu_ctx_switches"].sum(),
            top_cpu_str,  
            top_disco_str, 
            str(dado["df"]["total_processos"].sum()),
            str(dado["df"]["virtual_memory_usage"].max()),
            str(dado["df"]["disk_read_kbps"].max()),
            str(dado["df"]['disk_percent'].max()),
            str(dado["df"]["disk_write_kbps"].max()),
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

    dadosRansomware = {}

    trusted_final['timestamp'] = pd.to_datetime(trusted_final['timestamp'], format='%d/%m/%Y %H:%M:%S')

    for dado in dados:

        mac = dado["mac"]

        df_mac = trusted_final[trusted_final["id_mac"] == mac].copy()

        ultimo_timestamp = df_mac["timestamp"].max()
        df_mac = df_mac[df_mac["timestamp"] >= (ultimo_timestamp - pd.Timedelta(days=1))]

        df_mac['timestamp'] = df_mac['timestamp'].dt.strftime('%d/%m/%Y %H:%M:%S')

        df_mac['timestamp_dt'] = pd.to_datetime(df_mac['timestamp'], format='%d/%m/%Y %H:%M:%S')
        df_mac['timestamp_5min'] = df_mac['timestamp_dt'].dt.floor('5min')

        df_historico = df_mac.groupby('timestamp_5min', as_index=False).agg({
            'cpu_percent':          'max',
            'virtual_memory_usage': 'max',
            'disk_write_kbps':      'max',
            'disk_read_kbps':       'max',
            'total_processos':      'last',
        })

        df_historico['timestamp'] = df_historico['timestamp_5min'].dt.strftime('%d/%m/%Y %H:%M:%S')

        limite_cpu        = pesquisarComponente("Uso de CPU (%)", mac)
        limite_ram        = pesquisarComponente("Memoria Usada (%)", mac)
        limite_escrita_kb = pesquisarComponente("Escrita em Disco (KB/s)", mac)
        limite_leitura_kb = pesquisarComponente("Leitura em Disco (KB/s)", mac)

        ultima = df_mac.iloc[-1]

        maior_escrita = df_mac.loc[df_mac["disk_write_kbps"].idxmax()]

        score, nivel = calcularScore(ultima, limite_cpu, limite_ram, limite_escrita_kb, limite_leitura_kb)

        historico = []

        for _, linha in df_historico.iterrows():

            s, n = calcularScore(linha, limite_cpu, limite_ram, limite_escrita_kb, limite_leitura_kb)

            historico.append({
                "timestamp":            str(linha["timestamp"]),
                "cpu_percent":          round(float(linha["cpu_percent"]), 2),
                "virtual_memory_usage": round(float(linha["virtual_memory_usage"]), 2),
                "disk_write_kbps":      round(float(linha["disk_write_kbps"]), 2),
                "disk_read_kbps":       round(float(linha["disk_read_kbps"]), 2),
                "score":                s,
                "nivel":                n,
            })

        dadosRansomware[mac] = {
            "mac":                   mac,
            "ultima_atualizacao":    datetime.now(timezone(timedelta(hours=-3))).strftime('%d/%m/%Y %H:%M:%S'),
            "timestamp_leitura":     str(ultima["timestamp"]),
            "score":                 score,
            "nivel":                 nivel,
            "cpu_percent":           round(float(ultima["cpu_percent"]), 2),
            "virtual_memory_usage":  round(float(ultima["virtual_memory_usage"]), 2),
            "disk_write_kbps":       round(float(ultima["disk_write_kbps"]), 2),
            "disk_read_kbps":        round(float(ultima["disk_read_kbps"]), 2),
            "disk_percent":          round(float(ultima["disk_percent"]), 2),
            "top_3_processos_disco": str(maior_escrita["top_3_processos_disco"]),
            "limites": {
                "cpu":        limite_cpu,
                "ram":        limite_ram,
                "escrita_kb": limite_escrita_kb,
                "leitura_kb": limite_leitura_kb,
            },
            "historico": historico,
        }

    ransomware_buffer = json.dumps(dadosRansomware, ensure_ascii=False, indent=2)

    cliente_s3.put_object(
        Bucket=bucket,
        Key="client/ransomware.json",
        Body=ransomware_buffer.encode("utf-8"),
        ContentType="application/json",
    )

    print("ransomware.json salvo e enviado ao S3 client/")

    return {
        "statusCode": 200,
        "body": "ETL executado com sucesso"
    }