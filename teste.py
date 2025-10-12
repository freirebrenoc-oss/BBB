import streamlit as st
import requests

# ======================
# Configurações da Página
# ======================
st.set_page_config(
    page_title="Assistente Matinal 🌞",
    page_icon="🌅",
    layout="centered")

st.title("Assistente Matinal 🌞")
st.write("Bem-vindo! Digite seu nome abaixo para uma saudação personalizada.")

# ======================
# Entrada do Nome
# ======================
nome = st.text_input("Digite o seu nome aqui:")

if nome:
    st.success(f"OLÁ, {nome.upper()}! É UM PRAZER TE VER POR AQUI.")

    # ======================
    # Seleção de Serviço
    # ======================
    opcao = st.selectbox(
        "Escolha um serviço:",
        ["Selecione...", "Ver temperatura", "Ver umidade do ar", "Sugestão de roupa"]
    )

    if opcao != "Selecione...":
        st.info(f"Você escolheu: {opcao}")

        # ======================
        # Entrada da Cidade
        # ======================
        cidade = st.text_input("Digite a cidade ou endereço:", value="Rio de Janeiro")

        # ======================
        # Lendo as chaves seguras
        # ======================
        try:
            OPENWEATHER_KEY = st.secrets["api_keys"]["openweather"]
        except KeyError:
            st.error(
                "As chaves de API não foram encontradas em st.secrets. "
                "Configure-as em .streamlit/secrets.toml conforme instruções."
            )
            OPENWEATHER_KEY = ""

        # ======================
        # Serviço: Temperatura
        # ======================
        if opcao == "Ver temperatura" and cidade.strip() != "" and OPENWEATHER_KEY != "":
            try:
                url = f"https://api.openweathermap.org/data/2.5/weather?q={cidade}&units=metric&lang=pt_br&appid={OPENWEATHER_KEY}"
                resposta = requests.get(url)
                dados = resposta.json()

                if resposta.status_code == 200:
                    temp = dados["main"]["temp"]
                    clima = dados["weather"][0]["description"].capitalize()
                    st.success(f"🌡️ A temperatura em {cidade.title()} é {temp}°C e o clima está {clima}.")
                else:
                    st.error("Não foi possível encontrar a cidade. Verifique o nome e tente novamente.")
            except Exception as e:
                st.error(f"Ocorreu um erro ao consultar o clima: {e}")

        # ======================
        # Serviço: Umidade
        # ======================
        elif opcao == "Ver umidade do ar" and cidade.strip() != "" and OPENWEATHER_KEY != "":
            try:
                url = f"https://api.openweathermap.org/data/2.5/weather?q={cidade}&units=metric&lang=pt_br&appid={OPENWEATHER_KEY}"
                resposta = requests.get(url)
                dados = resposta.json()

                if resposta.status_code == 200:
                    umidade = dados["main"]["humidity"]
                    st.success(f"💧 A umidade do ar em {cidade.title()} é de {umidade}%.")
                else:
                    st.error("Não foi possível obter a umidade da cidade informada.")
            except Exception as e:
                st.error(f"Ocorreu um erro ao consultar a umidade: {e}")

        # ======================
        # Serviço: Sugestão de Roupa
        # ======================
        elif opcao == "Sugestão de roupa" and cidade.strip() != "" and OPENWEATHER_KEY != "":
            try:
                url = f"https://api.openweathermap.org/data/2.5/weather?q={cidade}&units=metric&lang=pt_br&appid={OPENWEATHER_KEY}"
                resposta = requests.get(url)
                dados = resposta.json()

                if resposta.status_code == 200:
                    temp = dados["main"]["temp"]
                    weather_desc = dados["weather"][0]["description"].lower()
                    if temp < 15:
                        sugest = "🧥 Frio intenso — use casaco pesado e, se possível, cachecol/luvas."
                    elif 15 <= temp <= 25:
                        sugest = "👕 Temperatura amena — roupas leves e um agasalho à mão."
                    else:
                        sugest = "🩳 Quente — use roupas leves e se hidrate bem."

                    if "chuva" in weather_desc:
                        sugest += " ☔ Leve guarda-chuva ou capa de chuva."

                    st.success(f"Em {cidade.title()}, a temperatura é {temp}°C.\n\n{ sugest }")
                else:
                    st.error("Não foi possível obter os dados do clima para gerar sugestão de roupa.")
            except Exception as e:
                st.error(f"Ocorreu um erro ao gerar sugestão de roupa: {e}")
                
else:
    st.info("Aguardando seu nome... 😊")
