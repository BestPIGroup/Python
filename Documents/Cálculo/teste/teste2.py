import csv;
from datetime import datetime;

def writer(peakRam, totalCPU, countRows):
    with open('resultado.csv', 'w', newline='') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',', quotechar=' ', quoting=csv.QUOTE_MINIMAL)
            spamwriter.writerow([f"Median CPU usage: {round((totalCPU/countRows),2)}\n Peak Ram usage: {round(peakRam, 2)}"])

def reader():
    
    peakRam = 0
    totalCPU = 0
    countRows = 0

    with open('eggs.csv', 'r', newline='') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    print(type(float(row[5])))
                    totalCPU += float(row[5])
                    countRows += 1
                    if float(row[6]) > peakRam:
                        peakRam = float(row[6])
    writer(peakRam, totalCPU, countRows)
reader()
                       

