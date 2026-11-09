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


# ===== ESTILO VISUAL (DESIGN SYSTEM COM VARIÁVEIS CSS) =====

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --background: #0F172A;
    --surface: #1E293B;
    --surface-hover: #263449;
    --border: #334155;
    --primary: #38BDF8;
    --text: #F1F5F9;
    --muted: #94A3B8;
    --success: #22C55E;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: var(--background);
    color: var(--text);
}

[data-testid="stHeader"] {
    background: transparent;
}

[data-testid="stSidebar"] {
    background: #111C30;
    border-right: 1px solid var(--border);
}

[data-testid="stSidebar"] * {
    color: var(--text);
}

h1, h2, h3 {
    color: var(--text) !important;
    font-weight: 700 !important;
    letter-spacing: -0.5px;
}

p, label {
    color: var(--muted);
}

/* Cartões (Metrics) */
div[data-testid="stMetric"] {
    background: var(--surface);
    border: 1px solid var(--border);
    padding: 22px;
    border-radius: 14px;
    transition: all 0.25s ease;
}

div[data-testid="stMetric"]:hover {
    background: var(--surface-hover);
    transform: translateY(-3px);
    border-color: var(--primary);
}

[data-testid="stMetricLabel"] {
    color: var(--muted) !important;
    font-size: 14px !important;
    font-weight: 600 !important;
}

[data-testid="stMetricValue"] {
    color: var(--text) !important;
    font-size: 29px !important;
    font-weight: 800 !important;
}

/* Container dos Gráficos */
[data-testid="stPlotlyChart"] {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 16px;
    transition: all 0.25s ease;
}

[data-testid="stPlotlyChart"]:hover {
    border-color: var(--primary);
}

/* Filtros */
div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 9px !important;
}

div[data-baseweb="tag"] {
    background: #334155 !important;
    border-radius: 6px !important;
}

div[data-baseweb="tag"] span {
    color: var(--text) !important;
}

button[kind="secondary"] {
    border-radius: 9px;
    border: 1px solid var(--border);
}

/* Tabela */
[data-testid="stDataFrame"] {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    overflow: hidden;
}

/* Botões */
.stButton > button {
    border-radius: 9px;
    font-weight: 600;
    transition: 0.2s ease;
}

.stButton > button:hover {
    border-color: var(--primary);
    color: var(--primary);
}

/* Animação */
@keyframes aparecer {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.main .block-container {
    animation: aparecer 0.5s ease;
    padding-top: 2rem;
}
</style>
""", unsafe_allow_html=True)


# ===== CONFIGURAÇÃO GLOBAL DE TEMA DOS GRÁFICOS =====

layout_dark = {
    "paper_bgcolor": "#1E293B",
    "plot_bgcolor": "#1E293B",
    "font": {
        "color": "#F1F5F9",
        "family": "Inter"
    },
    "margin": dict(l=25, r=25, t=50, b=35),
    "xaxis": {
        "showgrid": False,
        "color": "#94A3B8",
        "zeroline": False
    },
    "yaxis": {
        "gridcolor": "#334155",
        "color": "#94A3B8",
        "zeroline": False,
        "tickprefix": "R$ ",
        "separatethousands": True
    },
    "hoverlabel": {
        "bgcolor": "#0F172A",
        "font_color": "#F1F5F9",
        "bordercolor": "#38BDF8"
    }
}


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


# ===== INDICADORES (KPIs) =====

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
    "💰 Faturamento total",
    formatar_reais(faturamento_total)
)

col2.metric(
    "🛒 Vendas registradas",
    f"{quantidade_vendas:,}".replace(",", ".")
)

col3.metric(
    "📦 Unidades vendidas",
    f"{unidades_vendidas:,}".replace(",", ".")
)

col4.metric(
    "📊 Ticket médio",
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

        fig_bar = px.bar(
            faturamento_categoria,
            x="categoria",
            y="faturamento",
            title="Faturamento por categoria",
            color_discrete_sequence=["#38BDF8"]
        )

        fig_bar.update_traces(
            marker_line_width=0,
            texttemplate="R$ %{y:,.0f}",
            textposition="outside",
            textfont=dict(color="#F1F5F9", size=11),
            cliponaxis=False,
            hovertemplate="<b>%{x}</b><br>Faturamento: R$ %{y:,.2f}<extra></extra>"
        )

        fig_bar.update_layout(**layout_dark)

        st.plotly_chart(fig_bar, use_container_width=True, key="fig_bar")

    # ===== EVOLUÇÃO MENSAL =====

    with coluna_direita:
        vendas_filtradas["mes"] = (
            vendas_filtradas["data"]
            .dt.to_period("M")
            .astype(str)
        )

        vendas_por_mes = (
            vendas_filtradas
            .groupby("mes", as_index=False)["faturamento"]
            .sum()
            .sort_values("mes")
        )

        fig_linha = px.line(
            vendas_por_mes,
            x="mes",
            y="faturamento",
            title="Evolução mensal do faturamento",
            markers=True,
            color_discrete_sequence=["#38BDF8"]
        )

        fig_linha.update_traces(
            line=dict(width=3),
            marker=dict(size=8, color="#7DD3FC", line=dict(color="#1E293B", width=2)),
            hovertemplate="Mês: %{x}<br>Faturamento: R$ %{y:,.2f}<extra></extra>"
        )

        fig_linha.update_layout(**layout_dark)

        st.plotly_chart(fig_linha, use_container_width=True, key="fig_linha")


    # ===== TABELA DE DETALHAMENTO DE VENDAS =====

    st.divider()
    st.subheader("Detalhamento das vendas")

    df_exibicao = vendas_filtradas.drop(columns=["mes"], errors="ignore")

    st.dataframe(
        df_exibicao,
        use_container_width=True,
        hide_index=True,
        column_config={
            "data": st.column_config.DateColumn(
                "Data",
                format="DD/MM/YYYY"
            ),
            "produto": st.column_config.TextColumn(
                "Produto"
            ),
            "categoria": st.column_config.TextColumn(
                "Categoria"
            ),
            "quantidade": st.column_config.NumberColumn(
                "Quantidade",
                format="%d"
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

    st.caption(f"Exibindo {len(vendas_filtradas)} registros após a aplicação dos filtros.")