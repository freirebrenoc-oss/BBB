import streamlit as st
import requests

# ======================
# Configurações da Página
# ======================
st.set_page_config(
    page_title="Assistente Matinal 🌞",
    page_icon="🌅",
    layout="centered"
)

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
        ["Selecione...", "Ver temperatura", "Ver umidade do ar", "Ver trânsito", "Sugestão de roupa"]
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
            HERE_KEY = st.secrets["api_keys"]["here"]
        except Exception:
            st.error("As chaves de API não foram encontradas em st.secrets. Configure-as em .streamlit/secrets.toml")
            OPENWEATHER_KEY = ""
            HERE_KEY = ""

        # ======================
        # Serviço: Temperatura
        # ======================
        if opcao == "Ver temperatura":
            if cidade.strip() != "" and OPENWEATHER_KEY != "":
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
        elif opcao == "Ver umidade do ar":
            if cidade.strip() != "" and OPENWEATHER_KEY != "":
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
        elif opcao == "Sugestão de roupa":
            if cidade.strip() != "" and OPENWEATHER_KEY != "":
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

        # ======================
        # Serviço: Trânsito
        # ======================
        elif opcao == "Ver trânsito":
            if cidade.strip() != "" and HERE_KEY != "":
                try:
                    # Exemplo: geocoding para obter lat/lng
                    geo_url = f"https://geocode.search.hereapi.com/v1/geocode?q={cidade}&apiKey={HERE_KEY}"
                    geo_resp = requests.get(geo_url).json()
                    if geo_resp.get("items"):
                        lat = geo_resp["items"][0]["position"]["lat"]
                        lng = geo_resp["items"][0]["position"]["lng"]

                        # Fluxo de tráfego (simulado)
                        traffic_url = f"https://traffic.ls.hereapi.com/traffic/6.3/flow.json?prox={lat},{lng},1000&apiKey={HERE_KEY}"
                        traffic_resp = requests.get(traffic_url).json()

                        # Extraindo dados básicos (jam factor)
                        try:
                            cf0 = traffic_resp["RWS"][0]["RW"][0]["FIS"][0]["FI"][0]["CF"][0]
                            jam_factor = float(cf0.get("JF", 0))
                            speed = float(cf0.get("SU", 0))
                            free_speed = float(cf0.get("FF", 0))

                            if jam_factor < 2:
                                status = "Trânsito fluindo bem 🚗💨"
                            elif jam_factor < 6:
                                status = "Trânsito moderado 🚙"
                            else:
                                status = "Trânsito pesado 🚗🚗🚗"

                            st.subheader(f"Trânsito em {cidade.title()}")
                            st.info(f"{status}")
                            st.write(f"Velocidade média: {speed:.1f} km/h (livre seria {free_speed:.1f} km/h)")
                            st.write(f"Jam factor (0-10): {jam_factor}")
                        except Exception:
                            st.warning("Não foi possível interpretar detalhes do tráfego para este local. Mostrando dados simulados.")
                            st.write("Trânsito moderado nas principais vias.")
                    else:
                        st.error("Local não encontrado para consulta de trânsito.")
                except Exception as e:
                    st.error(f"Ocorreu um erro ao consultar trânsito: {e}")

else:
    st.info("Aguardando seu nome... 😊")





