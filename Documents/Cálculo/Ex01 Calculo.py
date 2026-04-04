a=2
if(input("F-String Ativada ou não?(1//0)")==1):
    potencia_ao_quadrado=a**2
    potencia_ao_cubo=a**3
    potencia_a_quarta=a**4
    print("Potência ao quadrado: ", potencia_ao_quadrado,"" \
    "Potência ao cubo: ", potencia_ao_cubo,"" \
    "Potência à quarta: ", potencia_a_quarta)
else:
    print(f'Potência ao quadrado: {a**2}\n')
    print(f'Potência ao cubo: {a**3}\n')
    print(f'Potência à quarta: {a**4}\n')