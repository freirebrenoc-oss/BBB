import streamlit as st
import pandas as pd
import plotly.express as px

# 1️⃣ Título do app
st.title("📊 Painel da Justiça Brasileira (CNJ - Justiça em Números)")

# 2️⃣ Carregar os dados do CSV local
# Ajuste separador e encoding conforme seu CSV
df = pd.read_csv(
    "BD_Consolidado_JF_Secao_23_Set_2025.csv",
    sep=';',         # Use ';' se os dados estiverem separados por ponto e vírgula
    encoding='utf-8' # Troque para 'latin1' se houver erro de caractere
)

# 3️⃣ Criar filtros interativos
anos = sorted(df["Ano"].unique())
tribunais = sorted(df["Tribunal"].unique())

ano_selecionado = st.selectbox("Selecione o ano:", anos)
tribunal_selecionado = st.selectbox("Selecione o tribunal:", tribunais)

# 4️⃣ Filtrar os dados
df_filtrado = df[(df["Ano"] == ano_selecionado) & (df["Tribunal"] == tribunal_selecionado)]

# 5️⃣ Mostrar informações gerais
st.subheader(f"Indicadores do {tribunal_selecionado} em {ano_selecionado}")

tempo_medio = df_filtrado["Tempo_Medio"].values[0]
taxa_cong = df_filtrado["Taxa_Congestionamento"].values[0]
casos_novos = df_filtrado["Casos_Novos"].values[0]

st.metric("Tempo médio de tramitação (dias)", f"{tempo_medio}")
st.metric("Taxa de congestionamento (%)", f"{taxa_cong}")
st.metric("Casos novos", f"{casos_novos}")

# 6️⃣ Gráfico comparativo por tribunal no mesmo ano
st.subheader("📈 Comparativo entre tribunais")
df_ano = df[df["Ano"] == ano_selecionado]
fig = px.bar(
    df_ano,
    x="Tribunal",
    y="Taxa_Congestionamento",
    title=f"Taxa de Congestionamento - {ano_selecionado}"
)
st.plotly_chart(fig)

# 7️⃣ Gráfico comparativo por ano do mesmo tribunal
st.subheader(f"📈 Evolução do {tribunal_selecionado} ao longo dos anos")
df_tribunal = df[df["Tribunal"] == tribunal_selecionado]
fig2 = px.line(
    df_tribunal,
    x="Ano",
    y="Tempo_Medio",
    title=f"Tempo médio de tramitação - {tribunal_selecionado}"
)
st.plotly_chart(fig2)
