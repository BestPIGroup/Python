import pandas as pd
from sqlalchemy import create_engine

# 1. Conectar ao MySQL e ler as regras de parametrização
engine = create_engine('mysql+mysqlconnector://usuario:senha@host/banco_de_dados')

# Tabela que define a categorização
df_regras = pd.read_sql('SELECT min_valor, max_valor, categoria FROM regras_categorizacao', engine)

# 2. Seu DataFrame original (ex: vendas)
data = {'venda_id': [1, 2, 3, 4],
        'valor': [50, 150, 600, 20]}
df = pd.DataFrame(data)

# 3. Preparar a categorização (pd.cut)
# Criamos uma lista de cortes (edges) baseada na tabela MySQL
# Adiciona o primeiro min e último max para definir os limites
bins = [0] + df_regras['max_valor'].tolist()
labels = df_regras['categoria'].tolist()

# 4. Criar a nova coluna categorizada
# include_lowest=True garante que o valor 0 seja incluído
df['categoria_venda'] = pd.cut(df['valor'], bins=bins, labels=labels, include_lowest=True)

print(df)
