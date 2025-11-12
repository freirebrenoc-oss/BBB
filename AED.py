import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import StringIO

# Configuração da página
st.set_page_config(page_title="Enforcement Pluralism — Custos de Transação", layout="wide")

# Título e Introdução
st.title("Enforcement Pluralism no Brasil — visualização dos custos de transação")

st.markdown(
    "Este app demonstra, com dados sintéticos, como a fragmentação institucional (ANTT, concessionárias, órgãos de trânsito) "
    "gera **custos de transação** — tempo e custo monetário — e como isso impacta a eficácia da sanção. "
    "Você pode fazer o **upload de um CSV** com as colunas esperadas ou usar o dataset de exemplo."
)

# Dataset sintético
@st.cache_data
def make_sample_data():
    """Cria um DataFrame de exemplo para o app."""
    data = [
        {"stage": "Detecção/Identificação", "actor": "Concessionária", "days": 10, "monetary_cost": 50, "cases": 1000},
        {"stage": "Comunicação ao Órgão de Trânsito", "actor": "Concessionária", "days": 15, "monetary_cost": 80, "cases": 800},
        {"stage": "Validação/Autuação", "actor": "Órgão de Trânsito (CONTRAN/SENATRAN)", "days": 40, "monetary_cost": 120, "cases": 700},
        {"stage": "Procedimentos administrativos", "actor": "Órgão de Trânsito", "days": 60, "monetary_cost": 200, "cases": 500},
        {"stage": "Execução/Multa aplicada", "actor": "Órgão de Trânsito", "days": 20, "monetary_cost": 0, "cases": 400},
        {"stage": "Recursos e contestações", "actor": "Consumidor / Tribunais", "days": 90, "monetary_cost": 300, "cases": 200},
    ]
    return pd.DataFrame(data)

# Carregamento de dados
sample_df = make_sample_data()
df = sample_df.copy() # Inicializa com dados de exemplo

st.sidebar.header("Dados")
upload = st.sidebar.file_uploader("Carregar CSV (opcional)", type=["csv"])

if upload is not None:
    try:
        uploaded_df = pd.read_csv(upload)
        # Checa colunas mínimas
        required = {"stage", "actor", "days", "monetary_cost", "cases"}
        if not required.issubset(set(uploaded_df.columns)):
            st.sidebar.error(f"O CSV deve conter as colunas: {sorted(required)}. Usando dados de exemplo.")
        else:
            df = uploaded_df.copy()
            # Garante que 'cases' seja int para o Sankey
            df['cases'] = df['cases'].astype(int)
            st.sidebar.success("CSV carregado com sucesso!")
    except Exception as e:
        st.sidebar.error("Erro ao ler CSV. Usando dados de exemplo.")
        st.sidebar.exception(e)

st.sidebar.markdown("---")
metric = st.sidebar.selectbox("Métrica para visualizar", ["days", "monetary_cost", "cases"], index=0)

# Layout principal
col1, col2 = st.columns([1, 1])

# --- Gráfico de Barras ---
with col1:
    st.subheader("Distribuição por Etapa — Gráfico de Barras")
    ordered = df.sort_values(by=metric, ascending=False)
    fig_bar = px.bar(
        ordered,
        x="stage",
        y=metric,
        color="actor",
        hover_data=["actor", "days", "monetary_cost", "cases"],
        labels={"stage": "Etapa", metric: metric.replace('_', ' ').title()},
        title=f"{metric.replace('_', ' ').title()} por Etapa e Ator"
    )
    fig_bar.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_bar, use_container_width=True)

# --- Gráfico Sankey ---
with col2:
    st.subheader("Sankey: Fluxo Institucional e Casos")
    
    # Nodes: lista única de atores + etapas
    nodes = list(df["actor"].unique()) + list(df["stage"].unique())
    node_idx = {n: i for i, n in enumerate(nodes)}

    # Sankey: Actor (Fonte) -> Stage (Destino) -> Cases (Valor)
    sources = [node_idx[row["actor"]] for _, row in df.iterrows()]
    targets = [node_idx[row["stage"]] for _, row in df.iterrows()]
    values = [int(row["cases"]) for _, row in df.iterrows()]

    sankey = go.Figure(go.Sankey(
        node = dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=nodes,
            # color="blue" # Opcional: para colorir todos os nós
        ),
        link = dict(
            source=sources,
            target=targets,
            value=values,
            hovertemplate='%{value} casos<extra></extra>'
        )
    ))
    sankey.update_layout(title_text="Fluxo: Ator (Fonte) → Etapa (Destino) — Casos (Volume)")
    st.plotly_chart(sankey, use_container_width=True)

st.markdown("---")

# Tabela de dados
st.subheader("Tabela de Dados")
st.dataframe(df, use_container_width=True)

# Download CSV
csv = df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Baixar CSV de Exemplo/Atual",
    data=csv,
    file_name="enforcement_data.csv",
    mime='text/csv'
)

st.markdown("---") 

# Interpretação
st.subheader("Interpretação e Contexto")
st.markdown(
    "A fragmentação entre identificação (**concessionária**), regulação (ANTT - *não explícito, mas no contexto*) e aplicação/execução (**CONTRAN/SENATRAN/Órgãos de trânsito**) "
    "cria etapas que aumentam **dias** e **custos** por caso. O **Sankey** mostra como o número de **casos** (multas/infrações) diminui a cada etapa do processo (perda de efetividade). "
    "Ajuste o CSV com dados reais (p.ex. tempo médio por procedimento, custo administrativo por caso) para estimar o impacto total e testar políticas alternativas (centralização, automação, acordos entre órgãos)."
)

st.markdown("---")

# Pequeno módulo para simular cenários (opcional)
st.subheader("Simulação de Cenários")
if st.checkbox("Simular cenários: reduzir dias em X% para etapas selecionadas"):
    
    # Certifique-se de usar o DataFrame original para a simulação, se não houver upload
    sim_df = df.copy() 

    # Adicionando uma coluna 'original_days' para comparação
    if 'original_days' not in sim_df.columns:
        sim_df['original_days'] = sim_df['days']

    pct = st.slider("Reduzir dias (%)", 0, 100, 20)
    
    # Opções para multiselect
    options = sorted(list(sim_df['actor'].unique()) + list(sim_df['stage'].unique()))
    actors_or_stages = st.multiselect(
        "Selecione atores/etapas para aplicar a redução:", 
        options=options, 
        default=[]
    )

    if st.button("Aplicar Simulação e Gerar Gráfico"):
        
        # Resetar 'days' para o valor original antes de aplicar nova simulação
        sim_df['days'] = sim_df['original_days']
        
        # Aplicar a simulação apenas nas linhas selecionadas
        mask = sim_df['actor'].isin(actors_or_stages) | sim_df['stage'].isin(actors_or_stages)
        sim_df.loc[mask, 'days'] = sim_df.loc[mask, 'days'] * (1 - pct/100)
        
        st.write(f"Simulação aplicada: redução de **{pct}%** nas linhas selecionadas.")
        
        # Gráfico pós-simulação
        fig_sim = px.bar(
            sim_df.sort_values(by='days', ascending=False), 
            x='stage', 
            y='days', 
            color='actor', 
            title='Dias Pós-Simulação vs. Dias Originais',
            labels={'days': 'Dias (Simulado)', 'stage': 'Etapa'}
        )
        
        # Adicionar o valor original como texto no gráfico para comparação
        fig_sim.update_traces(
            text=sim_df['original_days'], 
            textposition='outside'
        )
        
        st.plotly_chart(fig_sim, use_container_width=True)
        
        # Download do CSV simulado
        st.download_button(
            "Baixar CSV Simulado", 
            data=sim_df.to_csv(index=False).encode('utf-8'), 
            file_name='simulated_enforcement.csv', 
            mime='text/csv'
        )

