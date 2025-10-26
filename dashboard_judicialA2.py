import streamlit as st
import pandas as pd
import plotly.express as px

# 1️⃣ Título do app
st.title("📊 Painel da Justiça Brasileira (CNJ - Justiça em Números)")

# 2️⃣ Carregar os dados do CSV local com tratamento automático
# Tenta primeiro separador ';' e encoding 'utf-8'
try:
    df = pd.read_csv("BD_Consolidado_JF_Secao_23_Set_2025.csv", sep=';', encoding='utf-8')
except Exception:
    # Se der erro, tenta com encoding 'latin1' ou separador ','
    df = pd.read_csv("BD_Consolidado_JF_Secao_23_Set_2025.csv", sep=';', encoding='latin1')

# Remover espaços extras nos nomes das colunas
df.columns = df.columns.str.strip()

# Verifica se as colunas básicas existem
colunas_necessarias = ["Ano", "Tribunal", "Tempo_Medio", "Taxa_Congestionamento", "Casos_Novos"]
for col in colunas_necessarias:
    if col not in df.columns:
        st.error(f"Coluna '{col}' não encontrada no CSV. Verifique o arquivo.")
        st.stop()

# 3️⃣ Criar filtros interativos
anos = sorted(df["Ano"].unique())
tribunais = sorted(df["Tribunal"].unique())

ano_selecionado = st.selectbox("Selecione o ano:", anos)
tribunal_selecionado = st.selectbox("Selecione o tribunal:", tribunais)

# 4️⃣ Filtrar os dados
df_filtrado = df[(df["Ano"] == ano_selecionado) & (df["Tribunal"] == tribunal_selecionado)]

if df_filtrado.empty:
    st.warning("Nenhum dado encontrado para a combinação selecionada.")
else:
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
