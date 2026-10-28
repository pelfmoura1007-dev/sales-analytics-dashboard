import pandas as pd

# Caminho do arquivo CSV
ARQUIVO_VENDAS = "data/vendas.csv"


def carregar_vendas():
    vendas = pd.read_csv(ARQUIVO_VENDAS)

    # Converter a coluna de datas
    vendas["data"] = pd.to_datetime(vendas["data"])

    # Calcular o faturamento de cada venda
    vendas["faturamento"] = (
        vendas["quantidade"] * vendas["preco_unitario"]
    )

    return vendas
