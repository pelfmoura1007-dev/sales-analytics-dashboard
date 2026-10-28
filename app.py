
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

data_minima = vendas["data"].min().date()
data_maxima = vendas["data"].max().date()

categorias = sorted(vendas["categoria"].unique())
produtos = sorted(vendas["produto"].unique())


# ===== FUNÇÕES DOS FILTROS =====

def limpar_filtros():
    st.session_state["categorias"] = []
    st.session_state["produtos"] = []
    st.session_state["periodo"] = (data_minima, data_maxima)


def restaurar_filtros():
    st.session_state["categorias"] = categorias.copy()
    st.session_state["produtos"] = produtos.copy()
    st.session_state["periodo"] = (data_minima, data_maxima)


def atualizar_produtos():
    categorias_atuais = st.session_state["categorias"]

    produtos_disponiveis = vendas[
        vendas["categoria"].isin(categorias_atuais)
    ]["produto"].unique()

    st.session_state["produtos"] = [
        produto
        for produto in st.session_state["produtos"]
        if produto in produtos_disponiveis
    ]


# ===== INICIALIZAÇÃO DOS FILTROS =====

if "categorias" not in st.session_state:
    st.session_state["categorias"] = categorias.copy()

if "produtos" not in st.session_state:
    st.session_state["produtos"] = produtos.copy()

if "periodo" not in st.session_state:
    st.session_state["periodo"] = (data_minima, data_maxima)


# ===== ESTILO VISUAL =====

st.markdown("""
<style>
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"] {
        background-color: #0F172A;
        color: #F8FAFC;
    }

    [data-testid="stHeader"] {
        background-color: #0F172A;
    }

    [data-testid="stMain"] h1,
    [data-testid="stMain"] h2,
    [data-testid="stMain"] h3,
    [data-testid="stMain"] p,
    [data-testid="stMain"] label {
        color: #F8FAFC;
    }

    [data-testid="stSidebar"] {
        background-color: #111827;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label {
        color: #F8FAFC;
    }

    [data-testid="stMetric"] {
        background-color: #1E293B;
        border: 1px solid #334155;
        padding: 20px;
        border-radius: 12px;
    }

    [data-testid="stMetricLabel"] p {
        color: #CBD5E1 !important;
    }

    [data-testid="stMetricValue"] {
        color: #FFFFFF !important;
    }

    [data-testid="stPlotlyChart"] {
        background-color: #FFFFFF;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 8px;
    }

    [data-testid="stDataFrame"] {
        background-color: #FFFFFF;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)


# ===== CABEÇALHO =====

st.title("Sales Analytics Dashboard")
st.caption("Análise de desempenho, faturamento e vendas")

st.divider()


# ===== FILTROS LATERAIS =====

st.sidebar.title("Filtros")
st.sidebar.caption("Personalize os dados exibidos.")

col_limpar, col_restaurar = st.sidebar.columns(2)

col_limpar.button(
    "Limpar filtros",
    on_click=limpar_filtros,
    use_container_width=True
)

col_restaurar.button(
    "Restaurar padrão",
    on_click=restaurar_filtros,
    use_container_width=True
)

periodo = st.sidebar.date_input(
    "Período das vendas",
    min_value=data_minima,
    max_value=data_maxima,
    format="DD/MM/YYYY",
    key="periodo"
)

categorias_selecionadas = st.sidebar.multiselect(
    "Categorias",
    options=categorias,
    key="categorias",
    on_change=atualizar_produtos
)

produtos_disponiveis = sorted(
    vendas[
        vendas["categoria"].isin(categorias_selecionadas)
    ]["produto"].unique()
)

produtos_selecionados = st.sidebar.multiselect(
    "Produtos",
    options=produtos_disponiveis,
    key="produtos"
)


# ===== APLICAÇÃO DOS FILTROS =====

if isinstance(periodo, (tuple, list)) and len(periodo) == 2:
    data_inicio, data_fim = periodo
elif isinstance(periodo, (tuple, list)) and len(periodo) == 1:
    data_inicio = data_fim = periodo[0]
else:
    data_inicio, data_fim = data_minima, data_maxima

vendas_filtradas = vendas[
    (vendas["data"].dt.date >= data_inicio)
    & (vendas["data"].dt.date <= data_fim)
    & (vendas["categoria"].isin(categorias_selecionadas))
    & (vendas["produto"].isin(produtos_selecionados))
].copy()


# ===== INDICADORES =====

faturamento_total = vendas_filtradas["faturamento"].sum()
quantidade_vendas = len(vendas_filtradas)
unidades_vendidas = vendas_filtradas["quantidade"].sum()

ticket_medio = (
    faturamento_total / quantidade_vendas
    if quantidade_vendas > 0
    else 0
)


def formatar_reais(valor):
    return (
        f"R$ {valor:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Faturamento total",
    formatar_reais(faturamento_total)
)

col2.metric(
    "Registros de vendas",
    f"{quantidade_vendas:,}".replace(",", ".")
)

col3.metric(
    "Unidades vendidas",
    f"{unidades_vendidas:,}".replace(",", ".")
)

col4.metric(
    "Ticket médio por registro",
    formatar_reais(ticket_medio)
)


# ===== GRÁFICOS =====

st.divider()
st.subheader("Análise de vendas")

if vendas_filtradas.empty:
    st.warning(
        "Nenhuma venda encontrada. Ajuste os filtros "
        "ou clique em Restaurar padrão."
    )

else:
    coluna_esquerda, coluna_direita = st.columns(2)

    # ===== FATURAMENTO POR CATEGORIA =====

    with coluna_esquerda:
        faturamento_categoria = (
            vendas_filtradas
            .groupby("categoria", as_index=False)["faturamento"]
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
            text="faturamento",
            color="categoria",
            color_discrete_sequence=[
                "#2563EB", "#0D9488", "#F59E0B"
            ]
        )

        grafico_categoria.update_traces(
            texttemplate="R$ %{y:,.0f}",
            textposition="outside",
            textfont=dict(color="#0F172A", size=11),
            cliponaxis=False,
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Faturamento: R$ %{y:,.2f}"
                "<extra></extra>"
            )
        )

        grafico_categoria.update_layout(
            height=420,
            showlegend=False,
            font=dict(color="#0F172A", size=12),
            title=dict(font=dict(color="#0F172A", size=18)),
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF",
            margin=dict(l=20, r=35, t=65, b=35),
            xaxis=dict(
                title="Categoria",
                tickfont=dict(color="#0F172A"),
                title_font=dict(color="#0F172A"),
                showgrid=False
            ),
            yaxis=dict(
                title="Faturamento (R$)",
                tickfont=dict(color="#334155"),
                title_font=dict(color="#0F172A"),
                tickprefix="R$ ",
                separatethousands=True,
                gridcolor="#E2E8F0",
                rangemode="tozero"
            ),
            hoverlabel=dict(
                bgcolor="#FFFFFF",
                font_color="#0F172A"
            )
        )

        st.plotly_chart(
            grafico_categoria,
            use_container_width=True,
            key="grafico_categoria"
        )

    # ===== EVOLUÇÃO MENSAL =====

    with coluna_direita:
        vendas_filtradas["mes"] = (
            vendas_filtradas["data"]
            .dt.to_period("M")
            .astype(str)
        )

        faturamento_mensal = (
            vendas_filtradas
            .groupby("mes", as_index=False)["faturamento"]
            .sum()
            .sort_values("mes")
        )

        grafico_mensal = px.line(
            faturamento_mensal,
            x="mes",
            y="faturamento",
            title="Evolução mensal do faturamento",
            labels={
                "mes": "Mês",
                "faturamento": "Faturamento (R$)"
            },
            markers=True
        )

        grafico_mensal.update_traces(
            line=dict(color="#2563EB", width=3),
            marker=dict(
                size=9,
                color="#0D9488",
                line=dict(color="#FFFFFF", width=2)
            ),
            hovertemplate=(
                "<b>Mês: %{x}</b><br>"
                "Faturamento: R$ %{y:,.2f}"
                "<extra></extra>"
            )
        )

        grafico_mensal.update_layout(
            height=420,
            font=dict(color="#0F172A", size=12),
            title=dict(font=dict(color="#0F172A", size=18)),
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF",
            margin=dict(l=20, r=25, t=65, b=35),
            xaxis=dict(
                title="Mês",
                tickfont=dict(color="#0F172A"),
                title_font=dict(color="#0F172A"),
                showgrid=False
            ),
            yaxis=dict(
                title="Faturamento (R$)",
                tickfont=dict(color="#334155"),
                title_font=dict(color="#0F172A"),
                tickprefix="R$ ",
                separatethousands=True,
                gridcolor="#E2E8F0",
                rangemode="tozero"
            ),
            hoverlabel=dict(
                bgcolor="#FFFFFF",
                font_color="#0F172A"
            )
        )

        st.plotly_chart(
            grafico_mensal,
            use_container_width=True,
            key="grafico_mensal"
        )


    # ===== TABELA DE VENDAS =====

    st.divider()
    st.subheader("Detalhamento das vendas")

    st.dataframe(
        vendas_filtradas.drop(columns=["mes"], errors="ignore"),
        use_container_width=True,
        hide_index=True,
        column_config={
            "data": st.column_config.DateColumn(
                "Data",
                format="DD/MM/YYYY"
            ),
            "preco_unitario": st.column_config.NumberColumn(
                "Preço unitário",
                format="R$ %.2f"
            ),
            "faturamento": st.column_config.NumberColumn(
                "Faturamento",
                format="R$ %.2f"
            )
        }
    )

    st.caption(
        f"Exibindo {quantidade_vendas} registros após os filtros."
    )
