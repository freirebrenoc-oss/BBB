# arquivo: freeflow_costs_app.py
# Para executar: streamlit run freeflow_costs_app.py

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Análise de Custos — Sistema Free Flow", layout="wide")

st.title("📊 Comparativo de Custos — Modelo Tradicional x Free Flow")
st.markdown("""
Este app ilustra os custos de implantação e operação do sistema Free Flow,
com base nos dados simulados para a BR-101/RJ/SP (outubro/2019).

- **CAPEX**: investimento inicial (obras, terrenos, construção).
- **OPEX**: custos operacionais (pessoal, manutenção, transporte de valores, etc.).
""")

# ---- Dados básicos ----
data = {
    "Categoria": ["CAPEX", "OPEX"],
    "Modelo Tradicional (Praças)": [216.9, 100.0],   # valores em milhões de R$
    "Modelo Free Flow (Pórticos)": [30.7, 25.0]
}

df = pd.DataFrame(data)

# ---- Gráfico de barras comparativo ----
st.subheader("Comparativo de Custos Totais (em milhões de R$)")
fig_bar = px.bar(
    df.melt(id_vars="Categoria", var_name="Modelo", value_name="Custo (R$ milhões)"),
    x="Categoria",
    y="Custo (R$ milhões)",
    color="Modelo",
    barmode="group",
    text="Custo (R$ milhões)",
)
fig_bar.update_traces(texttemplate="%{text:.1f}", textposition="outside")
fig_bar.update_layout(yaxis_title="Custo (R$ milhões)", xaxis_title="")
st.plotly_chart(fig_bar, use_container_width=True)

# ---- Detalhamento do CAPEX Tradicional ----
st.subheader("Composição do CAPEX — Modelo Tradicional")

capex_data = pd.DataFrame({
    "Elemento": [
        "Obras civis (praças, cabines, infraestrutura)",
        "Desapropriação de terras",
        "Edificações das praças de pedágio",
        "Outros (equipamentos, sinalização, etc.)"
    ],
    "Custo (R$ milhões)": [160, 40, 16.9, 0]
})

fig_pie = px.pie(
    capex_data,
    names="Elemento",
    values="Custo (R$ milhões)",
    title="Distribuição dos custos de capital no modelo tradicional"
)
st.plotly_chart(fig_pie, use_container_width=True)

# ---- Eficiência e área ocupada ----
st.subheader("Efeitos adicionais do Free Flow")
st.markdown("""
- **Redução do CAPEX**: cerca de **-86%**.
- **Redução da área necessária**: **6,85 hectares a menos**.
- **Custo de edificação por praça (tradicional)**: R$ 7,6 milhões cada.
- **Custo médio por pórtico Free Flow (internacional)**: 100.000–150.000 EUR.
""")

# ---- Desempenho técnico ----
st.subheader("Desempenho técnico (dados de Set/2024)")
performance = pd.DataFrame({
    "Indicador": ["Taxa de detecção de veículos", "Taxa de leitura de placa (OCR)"],
    "Desempenho": [99.97, 99.55]
})
fig_perf = px.bar(performance, x="Indicador", y="Desempenho", text="Desempenho", color="Indicador")
fig_perf.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
fig_perf.update_layout(yaxis_title="%", title="Precisão do Sistema Free Flow")
st.plotly_chart(fig_perf, use_container_width=True)

# ---- Reflexão final ----
st.markdown("---")
st.markdown("""
### ⚖️ Interpretação
O Free Flow **reduz fortemente os custos de capital (CAPEX)** e **custos operacionais (OPEX)**, 
mantendo alto desempenho tecnológico.  
Contudo, no Brasil, o principal desafio **não é tecnológico**, e sim **institucional**:
garantir que quem utiliza a rodovia realmente **pague a tarifa**.

Isso envolve custos de **enforcement** — monitoramento, cobrança e penalização
de inadimplentes — que podem comprometer parte das economias obtidas no investimento inicial.
""")
