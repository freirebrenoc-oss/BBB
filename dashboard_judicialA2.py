import streamlit as st
import pandas as pd
import plotly.express as px

# 1️⃣ Título do app
st.title("📊 Dashboard CNJ Dinâmico")

# 2️⃣ Upload do CSV pelo usuário
uploaded_file = st.file_uploader("Escolha um arquivo CSV do CNJ", type="csv")

if uploaded_file:
    try:
        # Ler CSV com encoding seguro
        df = pd.read_csv(uploaded_file, sep=';', encoding='latin1')
    except:
        df = pd.read_csv(uploaded_file, sep=',', encoding='latin1')

    # Limpar nomes de colunas
    df.columns = df.columns.str.strip().str.replace("\n", " ").str.replace(" ", "_").str.replace("é","e").str.replace("ç","c")
    
    st.subheader("Colunas disponíveis no CSV")
    st.write(df.columns.tolist())

    # 3️⃣ Seleção de colunas para gráficos e métricas
    col_x = st.selectbox("Escolha a coluna para o eixo X (ex: Ano):", df.columns)
    col_y = st.selectbox("Escolha a coluna para os valores (ex: Tempo_Medio):", df.columns)

    # 4️⃣ Filtrar dados (opcional: escolha de valor único para filtro)
    filtro_col = st.selectbox("Filtrar por coluna (opcional):", ["Nenhum"] + list(df.columns))
    if filtro_col != "Nenhum":
        filtro_val = st.selectbox(f"Escolha o valor de {filtro_col}:", df[filtro_col].unique())
        df_filtrado = df[df[filtro_col] == filtro_val]
    else:
        df_filtrado = df.copy()

    if df_filtrado.empty:
        st.warning("Nenhum dado encontrado com os filtros selecionados.")
    else:
        # 5️⃣ Mostrar métricas básicas da coluna escolhida
        st.subheader(f"Métricas da coluna '{col_y}'")
        st.metric("Mínimo", df_filtrado[col_y].min())
        st.metric("Máximo", df_filtrado[col_y].max())
        st.metric("Média", round(df_filtrado[col_y].mean(),2))

        # 6️⃣ Gráfico interativo
        st.subheader(f"Gráfico de '{col_y}' vs '{col_x}'")
        fig = px.bar(df_filtrado, x=col_x, y=col_y, title=f"{col_y} por {col_x}")
        st.plotly_chart(fig)
