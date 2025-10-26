import streamlit as st
import pandas as pd
import plotly.express as px

# 1️⃣ Título do app
st.title("⚖️ Painel de Desempenho dos Tribunais Brasileiros (CNJ)")

# 2️⃣ Upload do CSV
uploaded_file = st.file_uploader("Escolha um arquivo CSV do CNJ", type="csv")

if uploaded_file:
    # 2a. Ler CSV com segurança (encoding automático)
    try:
        df = pd.read_csv(uploaded_file, sep=';', encoding='latin1')
    except:
        df = pd.read_csv(uploaded_file, sep=',', encoding='latin1')
    
    # 2b. Limpar nomes de colunas
    df.columns = df.columns.str.strip().str.replace("\n"," ").str.replace(" ","_").str.replace("é","e").str.replace("ç","c")
    
    # 3️⃣ Detectar possíveis indicadores disponíveis no CSV
    possiveis_indicadores = [
        "Numero_de_processos",
        "Tempo_medio_de_tramitacao",
        "Taxa_de_congestionamento",
        "Produtividade_de_magistrados",
        "Gastos_por_processo",
        "Taxa_de_solucao_de_processos"
    ]
    
    indicadores_disponiveis = [ind for ind in possiveis_indicadores if ind in df.columns]
    
    if len(indicadores_disponiveis) == 0:
        st.error("Nenhum dos indicadores principais foi encontrado no CSV.")
    else:
        st.sidebar.subheader("Escolha os indicadores para análise")
        indicadores_selecionados = st.sidebar.multiselect(
            "Selecione até 6 indicadores",
            options=indicadores_disponiveis,
            default=indicadores_disponiveis[:6]
        )
        
        # 4️⃣ Filtros por ano e tribunal se existirem
        if "Ano" in df.columns:
            anos = sorted(df["Ano"].unique())
            ano_selecionado = st.sidebar.selectbox("Selecione o ano:", anos)
            df = df[df["Ano"] == ano_selecionado]
        
        if "Tribunal" in df.columns:
            tribunais = sorted(df["Tribunal"].unique())
            tribunal_selecionado = st.sidebar.selectbox("Selecione o tribunal:", tribunais)
            df = df[df["Tribunal"] == tribunal_selecionado]
        
        # 5️⃣ Mostrar métricas
        st.subheader(f"Indicadores do tribunal selecionado")
        for ind in indicadores_selecionados:
            valor = df[ind].mean() if pd.api.types.is_numeric_dtype(df[ind]) else "N/A"
            st.metric(ind.replace("_"," "), round(valor,2) if isinstance(valor,float) else valor)
        
        # 6️⃣ Gráficos
        st.subheader("📈 Gráficos dos indicadores")
        for ind in indicadores_selecionados:
            if pd.api.types.is_numeric_dtype(df[ind]):
                fig = px.bar(df, x=df.index, y=ind, title=ind.replace("_"," "))
                st.plotly_chart(fig)
        
        # 7️⃣ Análise automática de desempenho
        st.subheader("💡 Análise automática de desempenho")
        analise = ""
        if "Taxa_de_congestionamento" in indicadores_selecionados and "Tempo_medio_de_tramitacao" in indicadores_selecionados:
            tc = df["Taxa_de_congestionamento"].mean()
            tm = df["Tempo_medio_de_tramitacao"].mean()
            if tc > 50 and tm > 365:
                analise += "- Tribunal apresenta **baixa eficiência**, com alta taxa de congestionamento e tempo médio de tramitação longo.\n"
            elif tc < 30 and tm < 180:
                analise += "- Tribunal apresenta **boa eficiência**, com baixa taxa de congestionamento e processos rápidos.\n"
            else:
                analise += "- Tribunal apresenta desempenho **intermediário**, há espaço para melhorias.\n"
        
        if "Produtividade_de_magistrados" in indicadores_selecionados:
            pm = df["Produtividade_de_magistrados"].mean()
            analise += f"- Produtividade média dos magistrados: {round(pm,2)} processos/julgado.\n"
        
        if "Gastos_por_processo" in indicadores_selecionados:
            gp = df["Gastos_por_processo"].mean()
            analise += f"- Gastos médios por processo: R$ {round(gp,2)}.\n"
        
        st.markdown(analise)
