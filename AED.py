""" Streamlit app: Enforcement pluralism & institutional transaction costs File: app.py

Como usar:

1. Crie um ambiente virtual (recomendado) e instale dependências: pip install streamlit pandas plotly


2. Execute: streamlit run streamlit_enforcement_pluralism_app.py



O app traz um dataset de exemplo (sintético) que modela as etapas do enforcement no Brasil (concessionária, ANTT, órgãos de trânsito) e mostra gráficos: barras e Sankey para visualizar como os custos de transação institucionais (tempo e custo direto) se distribuem entre atores e etapas.

Sugestões para GitHub:

Crie um repositório com: app.py, requirements.txt, README.md

requirements.txt: streamlit\npandas\nplotly


"""

import streamlit as st import pandas as pd import plotly.express as px import plotly.graph_objects as go from io import StringIO

st.set_page_config(page_title="Enforcement Pluralism — Custos de Transação", layout="wide")

st.title("Enforcement pluralism no Brasil — visualização dos custos de transação") st.markdown( "Este app demonstra, com dados sintéticos, como a fragmentação institucional (ANTT, concessionárias, órgãos de trânsito) gera custos de transação — tempo e custo monetário — e como isso impacta a eficácia da sanção.")

Dataset sintético (pode fazer upload de CSV com as colunas: stage, actor, days, monetary_cost, cases)

@st.cache_data def make_sample_data(): data = [ {"stage": "Detec\u00e7\u00e3o/Identifica\u00e7\u00e3o", "actor": "Concession\u00e1ria", "days": 10, "monetary_cost": 50, "cases": 1000}, {"stage": "Comunica\u00e7\u00e3o ao Órg\u00e3o de Tr\u00e2nsito", "actor": "Concession\u00e1ria", "days": 15, "monetary_cost": 80, "cases": 800}, {"stage": "Valida\u00e7\u00e3o/Autua\u00e7\u00e3o", "actor": "Órgão de Trânsito (CONTRAN/SENATRAN)", "days": 40, "monetary_cost": 120, "cases": 700}, {"stage": "Procedimentos administrativos", "actor": "Órgão de Trânsito", "days": 60, "monetary_cost": 200, "cases": 500}, {"stage": "Execu\u00e7\u00e3o/Multa aplicada", "actor": "Órgão de Trânsito", "days": 20, "monetary_cost": 0, "cases": 400}, {"stage": "Recursos e contesta\u00e7\u00f5es", "actor": "Consumidor / Tribunais", "days": 90, "monetary_cost": 300, "cases": 200}, ] return pd.DataFrame(data)

sample_df = make_sample_data()

st.sidebar.header("Dados") upload = st.sidebar.file_uploader("Carregar CSV (opcional)", type=["csv"]) if upload is not None: try: df = pd.read_csv(upload) # Checa colunas mínimas required = {"stage", "actor", "days", "monetary_cost", "cases"} if not required.issubset(set(df.columns)): st.sidebar.error(f"CSV deve conter as colunas: {sorted(required)}") df = sample_df.copy() else: df = df.copy() st.sidebar.success("CSV carregado com sucesso") except Exception as e: st.sidebar.error("Erro ao ler CSV: " + str(e)) df = sample_df.copy() else: df = sample_df.copy()

st.sidebar.markdown("---") metric = st.sidebar.selectbox("Métrica para visualizar", ["days", "monetary_cost", "cases"], index=0)

Main layout

col1, col2 = st.columns([1, 1])

with col1: st.subheader("Distribuição por etapa — gráfico de barras") ordered = df.sort_values(by=metric, ascending=False) fig_bar = px.bar(ordered, x="stage", y=metric, color="actor", hover_data=["actor", "days", "monetary_cost", "cases"], labels={"stage": "Etapa", metric: metric}, title=f"{metric} por etapa e ator") fig_bar.update_layout(xaxis_tickangle=-45) st.plotly_chart(fig_bar, use_container_width=True)

with col2: st.subheader("Sankey: fluxo institucional e perda de efetividade") # Construir sankey simples entre atores/stages # Nodes: lista única de atores + etapas nodes = list(df["actor"].unique()) + list(df["stage"].unique()) node_idx = {n: i for i, n in enumerate(nodes)}

# Como fonte, use actor; destino, use stage; value = cases
sources = [node_idx[row["actor"]] for _, row in df.iterrows()]
targets = [node_idx[row["stage"]] for _, row in df.iterrows()]
values = [int(row["cases"]) for _, row in df.iterrows()]

sankey = go.Figure(go.Sankey(
    node = dict(
        pad=15,
        thickness=20,
        line=dict(color="black", width=0.5),
        label=nodes,
    ),
    link = dict(
        source=sources,
        target=targets,
        value=values,
        hovertemplate='%{value} casos<extra></extra>'
    )
))
sankey.update_layout(title_text="Fluxo: quem identifica -> quem processa (casos)")
st.plotly_chart(sankey, use_container_width=True)

st.markdown("---")

st.subheader("Tabela de dados") st.dataframe(df)

Download CSV

csv = df.to_csv(index=False) st.download_button(label="Baixar CSV de exemplo", data=csv, file_name="enforcement_data.csv", mime='text/csv')

st.markdown("---") st.markdown("Como interpretar: A fragmenta\u00e7\u00e3o entre identifica\u00e7\u00e3o (concession\u00e1ria), regula\u00e7\u00e3o (ANTT) e aplica\u00e7\u00e3o/execu\u00e7\u00e3o (CONTRAN/SENATRAN/�rgãos de tr\u00e2nsito) cria etapas que aumentam dias e custos por caso. Ajuste o CSV com dados reais (p.ex. tempo m\u00e9dio por procedimento, custo administrativo por caso) para estimar o impacto total e testar pol\u00edticas alternativas (centraliza\u00e7\u00e3o, automa\u00e7\u00e3o, acordos entre órgãos).")

st.markdown("Extras para repo no GitHub:\n- Coloque este arquivo como app.py.\n- Adicione requirements.txt:\n  streamlit\n  pandas\n  plotly\n- Adicione README.md com instruções de execução e uma explicação do modelo de dados (colunas esperadas).")

Pequeno módulo para simular cenários (opcional)

if st.checkbox("Simular cenários: reduzir dias em X% para etapas selecionadas"): pct = st.slider("Reduzir dias (%)", 0, 100, 20) actors = st.multiselect("Selecione atores/etapas para aplicar redução (actor ou stage)", options=list(df['actor'].unique()) + list(df['stage'].unique())) if st.button("Aplicar simulação"): sim_df = df.copy() mask = sim_df['actor'].isin(actors) | sim_df['stage'].isin(actors) sim_df.loc[mask, 'days'] = sim_df.loc[mask, 'days'] * (1 - pct/100) st.write(f"Simulação aplicada: redução de {pct}% nas linhas selecionadas") fig_sim = px.bar(sim_df.sort_values(by='days', ascending=False), x='stage', y='days', color='actor', title='Dias pós-simulação') st.plotly_chart(fig_sim, use_container_width=True) st.download_button("Baixar CSV simulado", data=sim_df.to_csv(index=False), file_name='simulated_enforcement.csv', mime='text/csv')

Fim do app
