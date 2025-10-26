import streamlit as st
import requests

st.set_page_config(page_title="Consulta de Leis", page_icon="⚖️", layout="centered")

st.title("⚖️ Sistema de Consulta de Leis e Artigos")
st.write("Digite o número da lei (ex: 8078/1990) ou o tipo (ex: PL 1000/2022).")

query = st.text_input("Busca:", placeholder="Ex: Lei 8078/1990 ou PL 1000/2022")

if st.button("Buscar"):
    try:
        # Separar número e ano (caso o usuário digite '8078/1990')
        if "/" in query:
            numero, ano = query.replace("Lei", "").strip().split("/")
            url = f"https://dadosabertos.camara.leg.br/api/v2/proposicoes?siglaTipo=PL&numero={numero.strip()}&ano={ano.strip()}"
        else:
            st.error("Digite no formato correto: Lei XXXX/AAAA")
            st.stop()

        resposta = requests.get(url)
        dados = resposta.json()

        if not dados["dados"]:
            st.warning("❌ Nenhuma lei encontrada.")
        else:
            lei = dados["dados"][0]
            st.subheader(f"📜 {lei['siglaTipo']} {lei['numero']}/{lei['ano']}")
            st.write(f"**Ementa:** {lei['ementa']}")
            st.write(f"**Data de apresentação:** {lei['dataApresentacao']}")
            st.write(f"**Autor:** {lei['autor'] if 'autor' in lei else 'Não informado'}")
            
            # Botão para copiar citação
            citation = f"{lei['siglaTipo']} {lei['numero']}/{lei['ano']} – {lei['ementa']}"
            st.code(citation)
            st.download_button("📋 Copiar citação", citation)

    except Exception as e:
        st.error(f"Erro: {e}")
