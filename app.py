import streamlit as st
import plotly.express as px

from src.analise import carregar_vendas


# ===== CONFIGURAÇÃO DA PÁGINA =====

st.set_page_config(
    page_title="Sales Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

# ===== CARREGAMENTO DOS DADOS =====

vendas = carregar_vendas()

# ===== TÍTULO =====

st.title("Sales Analytics Dashboard")
st.caption("Painel de análise e desempenho de vendas")

st.divider()

# ===== INDICADORES =====

faturamento_total = vendas["faturamento"].sum()
quantidade_vendas = len(vendas)
unidades_vendidas = vendas["quantidade"].sum()
ticket_medio = faturamento_total / quantidade_vendas if quantidade_vendas else 0

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Faturamento total",
    f"R$ {faturamento_total:,.2f}"
)

col2.metric(
    "Quantidade de vendas",
    f"{quantidade_vendas:,}"
)

col3.metric(
    "Unidades vendidas",
    f"{unidades_vendidas:,}"
)

col4.metric(
    "Ticket médio",
    f"R$ {ticket_medio:,.2f}"
)

st.divider()

# ===== FATURAMENTO POR CATEGORIA =====

faturamento_categoria = (
    vendas.groupby("categoria", as_index=False)["faturamento"]
    .sum()
    .sort_values("faturamento", ascending=False)
)

grafico_categoria = px.bar(
    faturamento_categoria,
    x="categoria",
    y="faturamento",
    title="Faturamento por categoria",
    labels={
        "categoria": "Categoria",
        "faturamento": "Faturamento (R$)"
    },
    text_auto=".2s"
)

st.plotly_chart(grafico_categoria, use_container_width=True)

# ===== TABELA DE VENDAS =====

st.subheader("Dados das vendas")

st.dataframe(
    vendas,
    use_container_width=True,
    hide_index=True
)
