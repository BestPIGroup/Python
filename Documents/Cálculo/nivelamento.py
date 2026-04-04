import time

ex=int(input("Deseja usar 1-[ANÁLISE METEOROLÓGICA], 2-[INSS_INSPECTION 1.5.7] ou 3-[TOTVS.machine]?"))
print("Carregando programa...")
time.sleep(2)
print("Compilando código...")
time.sleep(1.3)
print("Iniciando...")
if ex==1:
    temp=int(input('Qual é a temperatura atual? '))
    print("Analisando clima...")
    time.sleep(3)
    if temp>21 and temp<=24:
        print("Temperatura agradável!")
    elif temp>24:
        print("HELL")
    else:
        print("Dê oi aos pinguins")
elif ex==2:
    rendafam=int(input("Qual é a renda total familiar do usuário? "))
    rendauser=int(input("Qual é a renda do usuário?"))
    print("Analisando eligibilidade...")
    time.sleep(2)
    if rendafam<=2100 and rendauser<=1050:
        print("Você tem direito ao benefício!")
    else:
        print("Burguês safado")
else:
    qtNotas=int(input("Quantas provas foram aplicadas? "))
    lista=[]
    media=0
    for ord_nota in range(qtNotas):
        nota=int(input(f"Qual é a {ord_nota+1}ª nota do aluno? "))
        lista.append(nota)
    for ord_media in range(qtNotas):
        media+=lista[ord_media]
    media=media/qtNotas
    print("Computando média final...")
    time.sleep(3)
    if media<6:
        print(f"Aluno reprovado com nota {media}")
    else:
        print(f"Aluno aprovado com media {media}")