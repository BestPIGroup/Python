Este é um repositório ETL para uso em servidores e na AWS. 

1 - Caso vá usar o script remotamente, coloque as suas credenciais AWS no .env.
        (Do contrário, comente as linhas 11-18 e 401 do escrita_escalavel.py.)
2 - Com base nas funções do escrita_escalavel.py, coloque as métricas desejadas no banco_escrita.json.
        (Lembre-se de colocar os parâmetros corretos!)
3 - Determine o intervalo entre registros na linha 399 e 376 do escrita_escalavel.py.
        (O tempo do time.sleep() multiplicado pelo range será o tempo de execução do código.)
4 - Se as leituras de algum item estiverem sendo contabilizadas desde o boot do SO, veja a função de trocas de contexto
        e aplique na sua função escolhida. Assim será contado entre cada registro do .csv


Victor Mattheus - Argos Project