import psutil
import time
from datetime import datetime
import csv


def leitura():
    with open('eggs.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
    for i in range(0, 5):
        time.sleep(1)
        hour=datetime.now()
        cpu=psutil.cpu_percent(interval=0.1)
        ram=psutil.virtual_memory().used
        disk=psutil.disk_usage('/').used
        time.sleep(1)
        with open('eggs.csv', 'a', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
            writer.writerow((hour.day, hour.month, hour.year, hour.hour, hour.minute, cpu, ram, disk))
leitura()
