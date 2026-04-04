import psutil
import time

print("Monitorando uso de memória RAM\n")

nome_digitado = input("Digite seu nome: ");

while True:
    mem = psutil.virtual_memory()
    porcentagem_memoria=mem.percent
    print(f"Uso: {porcentagem_memoria}%")
    print(f"Maquina do {nome_digitado}")

    if(porcentagem_memoria>30):
        print(f"""QUEIME
            QUEIME IMEDIATAMENTE""")

    time.sleep(2)