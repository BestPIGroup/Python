#victor matheus e arthur

agora={"ITSA4", "ECOR3", "TAEE11", "B3SA3", "VALE3"}
ativa={"B3SA3", "BBDC4", "BBSE3", "BRDT3", "TAEE11", "TRPL4", "VALE3", "VIVT3"}
genial={"CPFE3", "BEEF3", "CYRE3", "SAPT4", "TRPL4"}
easynvest={"B3SA3", "AGRO3", "COCA34", "TAEE11", "VALE3", "CPLE11", "ITSA4", "ABEV3"}
elite={"BBDC4", "BBSE3", "BRSR6", "EGIE3", "ITSA4", "SAPR11", "TAEE11", "TRPL4", "VIVT3", "VALE3"}
guide={"ALUP11", "BBAS3", "CYRE3", "CPFE3", "KLBN11", "PSSA3", "TIMS3", "VALE3"}
novafutura={"B3SA3", "CYRE3", "GGBR4", "VIVT3", "TRPL4"}
orama={"ABCB4", "BBDC4", "BEEF3", "CESP6", "EGIE3"}
corretoras= [agora, ativa, genial, easynvest, elite, guide, novafutura, orama]

def intersectGlobal():
    globalintersect=set(agora&ativa&genial&easynvest&elite&guide&novafutura&orama)
    print(globalintersect)
def intersectSpecific(c1, c2, c3, c4):
    specificintersect=c1&c2&c3&c4
    print(specificintersect)

def uniqueElementsGlobal():
    uniqueAgora=agora-(ativa|genial|easynvest|elite|guide|novafutura|orama)
    uniqueAtiva=ativa-(agora|genial|easynvest|elite|guide|novafutura|orama)
    uniqueGenial=genial-(agora|ativa|easynvest|elite|guide|novafutura|orama)
    uniqueEasyinvest=easynvest-(agora|genial|ativa|elite|guide|novafutura|orama)
    uniqueElite=elite-(agora|genial|easynvest|ativa|guide|novafutura|orama)
    uniqueGuide=guide-(agora|genial|easynvest|elite|ativa|novafutura|orama)
    uniqueNovafutura=novafutura-(agora|genial|easynvest|elite|guide|ativa|orama)
    uniqueOrama=orama-(agora|genial|easynvest|elite|guide|novafutura|ativa)
    print(uniqueAgora|uniqueAtiva|uniqueGenial|uniqueEasyinvest|uniqueElite|uniqueGuide|uniqueNovafutura|uniqueOrama)
def uniqueElementsSpecific(c1, c2, c3, c4):
    uniqueC1=c1-(c2|c3|c4)
    uniqueC2=c2-(c1|c3|c4)
    uniqueC3=c3-(c1|c2|c4)
    uniqueC4=c4-(c1|c2|c3)
    print(uniqueC1|uniqueC2|uniqueC3|uniqueC4)

def corretoraRelationsGlobal():
    msg=""
    for corretora in corretoras:
        for corretora2 in corretoras:
            if corretora.issubset(corretora2) and corretora!=corretora2:
                msg+=f"{corretora} é subset de {corretora2}"
    if msg == "":
        print(f"""Nenhuma corretora é subset de nenhuma corretora""")
    else:
        print(msg)
def corretoraRelationsSpecific(c1, c2, c3, c4):
    corretorasspecific=c1|c2|c3|c4
    msg=""
    for corretora in corretorasspecific:
        for corretora2 in corretorasspecific:
            if corretora.issubset(corretora2) and corretora!=corretora2:
                msg+=f"{corretora} é subset de {corretora2}\n"
    if msg == "":
        print(f"""Nenhuma corretora é subset de nenhuma corretora""")
    else:
        print(msg)
    
def corretorasOptions():
    print(f"""Selecione as corretoras a utilizar:
        1-agora
        2-ativa
        3-genial
        4-easynvest
        5-elite
        6-guide
        7-novafutura
        8-orama""")
   
    params = []
    for i in range(0,4):
        params.insert(i, corretoras[int(input())-1])
        
    menu(params[0], params[1], params[2], params[3])

def menu(c1, c2, c3, c4):
    print(c1, c2, c3, c4)
    nextFunction=input(f"""Selecione a função a executar:
                       1 - Intersect Global
                       2 - Intersect Specific
                       3 - Unique Elements Global
                       4 - Unique Elements Specific
                       5 - Corretora Relations Global
                       6 - Corretora Relations Specific
                       """)
    print(type(nextFunction) + nextFunction)
    if nextFunction == 1:
        intersectGlobal()
    elif nextFunction == 2:
        intersectSpecific(c1, c2, c3, c4)
    elif nextFunction == 3:
        uniqueElementsGlobal()
    elif nextFunction == 4:
        uniqueElementsSpecific(c1, c2, c3, c4)
    elif nextFunction == 5:
        corretoraRelationsGlobal()
    elif nextFunction == 6:
        corretoraRelationsSpecific(c1, c2, c3, c4)

corretorasOptions()