import psutil
import time
from datetime import datetime
import csv

#pid de gerenciamento de threads windows, importante para detectar problemas no SO como 
#conflito de driver ou problemas de hardware.
pid=4

def leitura():
    
    with open('eggs.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=' ',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(("dia", "mes", "ano", "hora", "minuto", "CPU", "RAM", "DISK", "PID"))
    for i in range(0, 50):
        hour=datetime.now()
        cpu=psutil.cpu_percent(interval=1)
        ram=round(psutil.virtual_memory().used/2**30, 2)
        disk=round(psutil.disk_usage('/').used/2**30, 2)
        p = psutil.Process(pid)
        processCPU = p.cpu_percent(0.1)
        time.sleep(1)
        with open('eggs.csv', 'a', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=' ',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
            writer.writerow((hour.day, hour.month, hour.year, hour.hour, hour.minute, cpu, ram, disk, processCPU))
leitura()

