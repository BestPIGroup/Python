import csv
import time
from datetime import datetime

nome = "isa"
arquivo_csv = "tratamento.csv"

while True:
        soma_cpu = 0
        contador = 0
        coluna_timestamp = 0
        coluna_disco_used = 7

        with open('monitoramento.csv', mode= "r") as file:
            leitura = csv.reader(file, delimiter=';', quotechar='|')
            next(leitura)

            for linha in leitura:
                if len(linha) > 2:
                    valor_cpu = float(linha[2])
                    if valor_cpu == 0:
                      continue
                    soma_cpu += valor_cpu
                    contador += 1
                if len(linha) > 3:
                    valor_memoria_total = float(linha[3])
                if len(linha) > 4:
                    valor_memoria_avaliable = float(linha[4])
                if len(linha) > 5:
                    valor_memoria_used = float(linha[5])
                if len(linha) > 6:
                    valor_memoria_free = float(linha[6])
                if len(linha) > 7:
                    valor_disco_total = float(linha[7])
                if len(linha) > 8:
                    valor_disco_used = float(linha[8])
                if len(linha) > 9:
                    valor_disco_free = float(linha[9])

            media_cpu = soma_cpu / contador
            porcento_memoria_used = (valor_memoria_used / valor_memoria_total) * 100
            porcento_memoria_available = (valor_memoria_avaliable / valor_memoria_total) * 100
            porcento_memoria_free = (valor_memoria_free / valor_memoria_total) * 100
            porcento_disco_free =  (valor_disco_free/ valor_disco_total) * 100
    
            time.sleep(2)

        with open(arquivo_csv, mode="a",encoding="utf-8") as file:
            escrever = csv.writer(file, delimiter=";")

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            media_cpu
            porcento_memoria_used
            porcento_memoria_available
            porcento_memoria_free

            escrever.writerow([nome, timestamp ,round(media_cpu, 2), round(porcento_memoria_used, 2), round(porcento_memoria_available, 2), round(porcento_memoria_free, 2), round(porcento_disco_free, 2)])

            print(f"""-----------------------------------------------------------
            Nome do servidor: {nome}
            Data e horario leitura: {timestamp}
            Uso médio da CPU sendo utilizada:{round(media_cpu, 2)}%
            Porcentagem de memoria RAM utilizada: {round(porcento_memoria_available, 2)} GB
            Porcentagem de memoria RAM livre: {round(porcento_memoria_free, 2)} GB
            Porcentagem de memoria RAM free: {round(porcento_disco_free, 2)}%
-----------------------------------------------------------""")