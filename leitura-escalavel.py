import csv
import time
from datetime import datetime 
import escrita_escalavel
arquivo_csv = "leitura-escalavel.csv"

with open('escalavel.csv', mode= "r") as file:
            leitura = csv.reader(file, delimiter=';', quotechar='|')
            next(leitura)
    
            for i in escrita_escalavel.lista_nomes:
                    print(escrita_escalavel.lista_nomes)