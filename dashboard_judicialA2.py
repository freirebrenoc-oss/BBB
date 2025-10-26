import streamlit as st
import pandas as pd
import plotly.express as px

# 1️⃣ Título do app
st.title("📊 Painel da Justiça Brasileira (CNJ - Justiça em Números)")

# 2️⃣ Carregar CSV com tratamento automático
try:
    df = pd.read_csv("BD_Consolidado_JF_Secao_23_Set_2025.csv", sep=';', encoding='utf-8')
except Exception:
    df = pd.read_csv("BD_Consolidado_JF_Secao_23_Set_2025.csv", sep=';', encoding='latin1')

# 3️⃣ Limpar nomes das colunas
df.columns = df.columns.str.strip()  # remove espaços
df.columns = df.columns.str.replace("\n", "")  # remove quebras de linha
df.columns = df.columns.str.replace(" ", "_")  # substitui espaços por _
df.columns = df.columns.str.replace("é", "e")  # substitui acentos
df.columns = df.columns.str.replace("ç", "c")

# 4️⃣ Renomear colunas para padronizar (ajuste conforme seu CSV)
colunas_esperadas = {
    "Ano": "Ano",
    "Tribunal": "Tribunal",
    "Tempo_Medio": "Tempo_Medio",
    "Taxa_Congestionamento": "Taxa_Congestionamento",
    "Casos_Novos": "Casos_Novos"
}

for col in colunas_esperadas.keys():
    if col not in df.columns:
        # Tenta encontrar a coluna parecida
        for c in df.columns:
            if col.lower() in c.lower():
                df.rename(columns={c: col}, inplace=True)

# Verificar se todas as colunas agora existem
for col in colunas_esperadas.values():
    if col not in df.columns:
        st.error(f"Coluna '{col}' não encontrada no CSV. Verifique o arquivo.")
        st.stop()

# 5️⃣ Criar filtros interativos
anos = sorted(df["Ano"].unique())
tribunais = sorted(df["Tribunal"].unique())

ano_selecionado = st.selectbox("Selecione o ano:", anos)
tribunal_selecionado = st.selectbox("Selecione o tribunal:", tribunais)

# 6️⃣ Filtrar os dados
df_filtrado = df[(df["Ano"] == ano_selecionado) & (df["Tribunal"] == tribunal_selecionado)]

if df_filtrado.empty:
    st.warning("Nenhum dado encontrado para a combinação selecionada.")
else:
    # 7️⃣ Mostrar informações gerais
    st.subheader(f"Indicadores do {tribunal_selecionado} em {ano_selecionado}")

    tempo_medio = df_filtrado["Tempo_Medio"].values[0]
    taxa_cong = df_filtrado["Taxa_Congestionamento"].values[0]
    casos_novos = df_filtrado["Casos_Novos"].values[0]

    st.metric("Tempo médio de tramitação (dias)", f"{tempo_medio}")
    st.metric("Taxa de congestionamento (%)", f"{taxa_cong}")
    st.metric("Casos novos", f"{casos_novos}")

    # 8️⃣ Gráfico comparativo por tribunal no mesmo ano
    st.subheader("📈 Comparativo entre tribunais")
    df_ano = df[df["Ano"] == ano_selecionado]
    fig = px.bar(
        df_ano,
        x="Tribunal",
        y="Taxa_Congestionamento",
        title=f"Taxa de Congestionamento - {ano_selecionado}"
    )
    st.plotly_chart(fig)

    # 9️⃣ Gráfico comparativo por ano do mesmo tribunal
    st.subheader(f"📈 Evolução do {tribunal_selecionado} ao longo dos anos")
    df_tribunal = df[df["Tribunal"] == tribunal_selecionado]
    fig2 = px.line(
        df_tribunal,
        x="Ano",
        y="Tempo_Medio",
        title=f"Tempo médio de tramitação - {tribunal_selecionado}"
    )
    st.plotly_chart(fig2)
