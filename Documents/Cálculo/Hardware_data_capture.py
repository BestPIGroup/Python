import psutil
import time
import csv
from datetime import datetime
import os

data = ["USER","DATETIME","CPU","RAM","MEM"]

arquivoCSV = 'Hardware_data.csv'

if os.path.exists(arquivoCSV) == False:

    with open(arquivoCSV, mode = "w", newline='') as arq:

            escritor = csv.writer(arq)
            escritor.writerow(data)

while True:

    mem = (psutil.disk_usage('/'))
    ram = psutil.virtual_memory()
    cpu = psutil.cpu_percent(interval=1, percpu=False)
    date = datetime.now()
    usuario = os.getlogin()

    print (usuario)

    data = [usuario,date.strftime("%Y-%m-%d %H:%M:%S"),cpu,round(ram.used/(1024**3),2),mem.percent]

    with open(arquivoCSV, mode = "a", newline='') as arq:

        escritor = csv.writer(arq)
        escritor.writerow(data)

    time.sleep(3)
