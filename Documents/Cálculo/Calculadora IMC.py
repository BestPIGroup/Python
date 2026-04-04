DEEPBLUE = "\x1B[38;5;18m"
BLUE = "\x1B[38;5;27m"
LIGHTBLUE = "\x1B[38;5;12m"
GREEN = "\x1B[38;5;46m"
YELLOW = "\x1B[38;5;226m"
ORANGE = "\x1B[38;5;208m"
DEEPRED = "\x1B[38;5;160m"
RED = "\x1B[38;5;88m"
WHITE = "\x1b[37m"

def CalcIMC(): 
    peso=float(input("Qual é o seu peso em kg?"))
    altura=float(input("Qual é a sua altura em m?"))
    imc=peso/altura**2
    if(imc<=16):
        print(f"""{DEEPBLUE} Seu IMC é {imc} - Baixo Peso Muito Grave""")
    elif(imc<=17):
        print(f"""{BLUE} Seu IMC é {imc} - Baixo Peso Grave""")
    elif(imc<=18):
        print(f"""{LIGHTBLUE} Seu IMC é {imc} - Peso Ideal""")
    elif(imc<=25):
        print(f"""{GREEN} Seu IMC é {imc} - Peso Ideal""")
    elif(imc<=30):
        print(f"""{YELLOW} Seu IMC é {imc} - Sobrepeso""")
    elif(imc<=35):
        print(f"""{ORANGE} Seu IMC é {imc} - Obesidade Grau I""")
    elif(imc<=40):
        print(f"""{RED} Seu IMC é {imc} - Obesidade Grau II""")
    else:
        print(f"""{DEEPRED} Seu IMC é {imc} - Obesidade Mórbida""") 
    if(input(f"""{WHITE}Deseja recalcular IMC?(S/N)""")=="S"):
        CalcIMC()
    else:
        print("Encerrando a calculadora")
CalcIMC()