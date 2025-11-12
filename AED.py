# arquivo: freeflow_regulacao_antt.py

import streamlit as st
import pandas as pd
import plotly.express as px

# ===========================
# TÍTULO E INTRODUÇÃO
# ===========================
st.title("Sistema Free Flow no Brasil: Custos e Regulação da ANTT")
st.markdown("""
Este painel interativo mostra, com base em **dados reais e extraídos do Sandbox Regulatório da ANTT (2024)**, 
como o sistema *Free Flow* reduz drasticamente os custos de capital (CAPEX) e mantém sustentabilidade econômica 
mesmo diante da inadimplência — desde que exista **enforcement regulatório eficiente**.
""")

# ===========================
# GRÁFICO 1: CAPEX - COMPARAÇÃO
# ===========================
st.header("1️⃣ Comparação de CAPEX — Modelo Tradicional x Free Flow")

capex_data = pd.DataFrame({
    "Modelo": ["Tradicional (3 Praças)", "Free Flow (3 Pórticos)"],
    "Custo Total (R$ milhões)": [216.9, 30.7],
    "Redução (%)": [0, 86]
})

fig1 = px.bar(
    capex_data,
    x="Modelo",
    y="Custo Total (R$ milhões)",
    text="Custo Total (R$ milhões)",
    color="Modelo",
    color_discrete_sequence=["#d62728", "#2ca02c"],
    title="Redução de CAPEX com o Sistema Free Flow"
)
fig1.update_traces(texttemplate="R$ %{y:.1f} mi", textposition="outside")
fig1.update_layout(yaxis_title="Custo Total (milhões R$)", xaxis_title=None)

st.plotly_chart(fig1, use_container_width=True)

st.markdown("""
O modelo tradicional de praças de pedágio apresenta **CAPEX total de R$ 216,9 milhões**, 
enquanto o sistema Free Flow reduz o custo para **R$ 30,7 milhões** — uma **economia de 86%**.  
Essa redução ocorre pela eliminação das obras civis, da desapropriação de terras e da construção de cabines físicas.
""")

# ===========================
# GRÁFICO 2: INADIMPLÊNCIA E RECEITA
# ===========================
st.header("2️⃣ Inadimplência e Sustentabilidade Econômica")

inad_data = pd.DataFrame({
    "Cenário": [
        "Impontualidade (média 2024)",
        "Inadimplência Acumulada",
        "Inadimplência Mensal (Set/2024)"
    ],
    "Taxa (%)": [11.85, 8.03, 9.09]
})

# Receita bruta hipotética
receita_bruta = 100  # em milhões R$
inad_data["Receita Líquida (R$ mi)"] = receita_bruta * (1 - inad_data["Taxa (%)"]/100)

fig2 = px.bar(
    inad_data,
    x="Cenário",
    y="Receita Líquida (R$ mi)",
    text="Receita Líquida (R$ mi)",
    color="Taxa (%)",
    color_continuous_scale="RdYlGn_r",
    title="Efeito da Inadimplência sobre a Receita — e o papel da regulação da ANTT"
)
fig2.update_traces(texttemplate="R$ %{y:.1f} mi", textposition="outside")
fig2.update_layout(yaxis_title="Receita Líquida (milhões R$)", xaxis_title=None)

st.plotly_chart(fig2, use_container_width=True)

st.markdown("""
Os dados do **Sandbox Regulatório da ANTT (2024)** indicam:
- **Taxa de impontualidade:** 11,8%–11,9% (pagamentos fora do prazo);  
- **Taxa de inadimplência acumulada:** 8,03%;  
- **Taxa de inadimplência mensal (set/2024):** 9,09% (média trimestral 7,75%).  

Apesar desses índices, o **Free Flow permanece financeiramente vantajoso**:  
mesmo com até 9% de inadimplência, a **economia de CAPEX e OPEX supera as perdas de arrecadação**.

A **regulação eficiente da ANTT** — com notificações automáticas, integração com SENATRAN/RENAINF, 
e autuação por infração grave (Lei nº 14.157/2021 e Resoluções CONTRAN nº 984/2022 e 1013/2024) — 
atua para reduzir gradualmente a inadimplência e assegurar a sustentabilidade do modelo.
""")

# ===========================
# CONCLUSÃO
# ===========================
st.header("📈 Conclusão")
st.markdown("""
O **desafio do Free Flow no Brasil não é tecnológico**, mas **institucional e comportamental**: garantir que quem passa, pague.  
A tecnologia já entrega taxas de leitura de **99,55% (OCR)** e **99,97% (detecção de veículos)**.

Assim, o verdadeiro ponto crítico é o **enforcement regulatório**.  
Quando bem estruturado — como vem sendo aprimorado pela **ANTT** —, 
ele é capaz de **superar o problema da inadimplência**, garantindo a **viabilidade econômica e ambiental** do sistema Free Flow.
""")
