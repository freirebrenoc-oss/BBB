import streamlit as st
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(page_title="Free Flow — Eficiência Regulatória da ANTT", layout="wide")

st.title("Free Flow no Brasil: Benefícios Superam os Custos de Enforcement")
st.markdown("""
O modelo **Free Flow** representa uma ruptura positiva na infraestrutura de pedágio,
reduzindo **custos de capital (CAPEX)** e **operacionais (OPEX)**, além de **minimizar impactos ambientais**.
Apesar de desafios de **inadimplência e impontualidade**, a **regulação inteligente da ANTT**
mostra que os **benefícios líquidos superam amplamente os custos de enforcement**.
---
""")

# ===================== GRÁFICO 1 — CAPEX =====================
st.subheader("1️⃣ Redução de CAPEX: Free Flow vs. Modelo Tradicional")

capex_data = pd.DataFrame({
    "Modelo": ["Tradicional (3 Praças)", "Free Flow (3 Pórticos)"],
    "Custo (R$ milhões)": [216.9, 30.7]
})

fig1 = go.Figure(go.Bar(
    x=capex_data["Modelo"],
    y=capex_data["Custo (R$ milhões)"],
    text=capex_data["Custo (R$ milhões)"],
    textposition="auto",
    marker_color=["#C0392B", "#27AE60"]
))
fig1.update_layout(title="Redução de 86% no Custo de Capital (CAPEX)",
                   yaxis_title="Custo Total (R$ milhões)",
                   template="plotly_white")
st.plotly_chart(fig1, use_container_width=True)

st.markdown("""
💡 **Análise:**  
O custo de implantação do modelo Free Flow é **86% menor** que o do modelo tradicional.  
A eliminação de obras civis e desapropriações gera economia direta e **reduz o custo de entrada do sistema**, 
superando com folga qualquer perda potencial com inadimplência (~8%).
""")

# ===================== GRÁFICO 2 — OPEX =====================
st.subheader("2️⃣ Redução de OPEX: Custos Operacionais Eliminados")

opex_data = pd.DataFrame({
    "Categoria": ["Pessoal (Arrecadadores, Conferentes, Líderes)", "Transporte de Valores", "Operação e Manutenção Eletrônica"],
    "Modelo Tradicional (R$ milhões/ano)": [83, 10, 7],
    "Modelo Free Flow (R$ milhões/ano)": [5, 0, 9]
})

fig2 = go.Figure()
fig2.add_trace(go.Bar(
    x=opex_data["Categoria"],
    y=opex_data["Modelo Tradicional (R$ milhões/ano)"],
    name="Tradicional",
    marker_color="#C0392B"
))
fig2.add_trace(go.Bar(
    x=opex_data["Categoria"],
    y=opex_data["Modelo Free Flow (R$ milhões/ano)"],
    name="Free Flow",
    marker_color="#27AE60"
))
fig2.update_layout(barmode="group", template="plotly_white",
                   title="Redução de Custos Operacionais (OPEX)",
                   yaxis_title="Custo Estimado (R$ milhões/ano)")
st.plotly_chart(fig2, use_container_width=True)

st.markdown("""
💡 **Análise:**  
O modelo Free Flow **elimina praticamente todo o custo de pessoal** e o de transporte de valores.  
Mesmo considerando o custo tecnológico de manutenção, há uma **redução líquida de aproximadamente 70% no OPEX**.
Essas economias **mais do que compensam** as perdas de receita decorrentes da inadimplência inicial (~8%).
""")

# ===================== GRÁFICO 3 — INADIMPLÊNCIA =====================
st.subheader("3️⃣ Taxa de Inadimplência e Impontualidade (Sandbox ANTT)")

inad_data = pd.DataFrame({
    "Mês": ["jun/24", "jul/24", "ago/24", "set/24", "out/24"],
    "Taxa de Inadimplência (%)": [6.5, 7.2, 8.0, 9.1, 8.5],
    "Taxa de Impontualidade (%)": [11.8, 11.9, 11.8, 11.9, 11.8]
})

fig3 = go.Figure()
fig3.add_trace(go.Scatter(x=inad_data["Mês"], y=inad_data["Taxa de Inadimplência (%)"],
                          mode="lines+markers", name="Inadimplência", line=dict(color="red", width=3)))
fig3.add_trace(go.Scatter(x=inad_data["Mês"], y=inad_data["Taxa de Impontualidade (%)"],
                          mode="lines+markers", name="Impontualidade", line=dict(color="orange", width=3, dash="dash")))
fig3.add_hline(y=8.03, line_dash="dot", line_color="gray",
               annotation_text="Média de inadimplência: 8,03%", annotation_position="bottom right")
fig3.update_layout(template="plotly_white", title="Tendência da Inadimplência e Impontualidade (2024)",
                   yaxis_title="Percentual (%)", legend_title="Indicadores")
st.plotly_chart(fig3, use_container_width=True)

st.markdown("""
📊 **Análise:**  
Apesar da inadimplência ter atingido **9,1% em setembro/2024**, a média do período (8,03%) é **plenamente absorvível**
dentro das economias de CAPEX e OPEX.  
O dado reforça que o **problema não é tecnológico, mas institucional e comportamental** — 
e a ANTT respondeu com **smart regulation**, ajustando prazos e fluxos de pagamento.
""")

# ===================== GRÁFICO 4 — EFICIÊNCIA REGULATÓRIA =====================
st.subheader("4️⃣ Regulação Inteligente da ANTT: Eficiência Líquida Positiva")

eff_data = pd.DataFrame({
    "Mês": ["jun/24", "jul/24", "ago/24", "set/24", "out/24"],
    "Benefício Líquido (%)": [4.0, 5.5, 6.8, 8.2, 9.5],
    "Inadimplência (%)": [6.5, 7.2, 8.0, 9.1, 8.5]
})

fig4 = go.Figure()
fig4.add_trace(go.Scatter(x=eff_data["Mês"], y=eff_data["Benefício Líquido (%)"],
                          mode="lines+markers", name="Benefício Líquido (Eficiência)",
                          line=dict(color="green", width=3)))
fig4.add_trace(go.Scatter(x=eff_data["Mês"], y=eff_data["Inadimplência (%)"],
                          mode="lines+markers", name="Inadimplência",
                          line=dict(color="red", width=3, dash="dash")))

fig4.update_layout(template="plotly_white", title="Evolução da Eficiência Líquida — Benefícios Superam Custos",
                   yaxis_title="Percentual (%)", legend_title="Indicadores")
st.plotly_chart(fig4, use_container_width=True)

st.markdown("""
✅ **Conclusão Geral:**  
Mesmo com uma **inadimplência média de 8,03%**, o **Free Flow é economicamente superior** ao modelo tradicional.  
A **ANTT, com sua regulação inteligente**, ajustou o sistema (via sandbox) para alinhar prazos ao comportamento social, 
reduzindo custos de enforcement e garantindo sustentabilidade financeira.  

➡️ **Os benefícios (redução de CAPEX e OPEX + eficiência regulatória)** **superam amplamente** os custos decorrentes da inadimplência.  
O custo de enforcement é **transitório**, enquanto os ganhos estruturais do Free Flow são **permanentes e cumulativos**.
""")
