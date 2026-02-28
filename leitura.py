import csv
import time
from datetime import datetime
import escrita

lista_cpu = []

arquivo_csv = "tratamento.csv"

while True:
        soma_cpu = 0
        contador = 0

        with open('monitoramento.csv', newline='') as file:
            leitura = csv.reader(file, delimiter=';', quotechar='|')
            next(leitura)

            for linha in leitura:
                if len(linha) > 1:
                    valor_cpu = float(linha[1])
                    if valor_cpu == 0:
                      continue
                    soma_cpu += valor_cpu
                    contador += 1
                elif len(linha) > 2:
                    valor_memoria_avaliable = float(linha[2])
                    if valor_memoria_avaliable == 0:
                      continue
                elif len(linha) > 3:
                    valor_memoria_used = float(linha[3])
                    if valor_memoria_used == 0:
                      continue
                    print("Ta dando certo ler")
            
        
            media_cpu = soma_cpu / contador
            memoria_disponivel = valor_memoria_avaliable / escrita.memoria_total_gb * 100
            time.sleep(2)

        with open(arquivo_csv, mode="a",encoding="utf-8") as file:
            escrever = csv.writer(file, delimiter=";")

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            media_cpu
            memoria_disponivel

            escrever.writerow([timestamp ,round(media_cpu, 2), round(memoria_disponivel)])

            print("Ta dando certo escrever")