import streamlit as st
import requests
import random

# ======================
# Configurações da Página
# ======================
st.set_page_config(
    page_title="Assistente Matinal 🌞",
    page_icon="🌅",
    layout="centered"
)

st.title("Assistente Matinal 🌞")
st.write("Bem-vindo! Digite seu nome abaixo para começar o dia com boas energias! 💫")

# ======================
# Entrada do Nome
# ======================
nome = st.text_input("Digite o seu nome aqui:")

if nome:
    st.success(f"OLÁ, {nome.upper()}! ☀️ É UM PRAZER TE VER POR AQUI.")

    # ======================
    # Entrada da Cidade
    # ======================
    cidade = st.text_input("Digite a cidade ou endereço:", value="Rio de Janeiro")

    # ======================
    # Lendo a chave da API
    # ======================
    try:
        # Caso tenha configurado direto como openweather="sua_chave" no Streamlit Cloud
        OPENWEATHER_KEY = st.secrets["openweather"]
    except KeyError:
        st.error("A chave da API não foi encontrada em st.secrets. Configure-a corretamente.")
        OPENWEATHER_KEY = ""

    # ======================
    # Consultar clima
    # ======================
    if OPENWEATHER_KEY and cidade.strip():
        try:
            url = f"https://api.openweathermap.org/data/2.5/weather?q={cidade}&units=metric&lang=pt_br&appid={OPENWEATHER_KEY}"
            resposta = requests.get(url)
            dados = resposta.json()

            if resposta.status_code == 200:
                temp = dados["main"]["temp"]
                umidade = dados["main"]["humidity"]
                clima = dados["weather"][0]["description"].capitalize()
                weather_desc = dados["weather"][0]["description"].lower()

                # ===== Temperatura =====
                st.subheader("🌡️ Temperatura")
                st.success(f"A temperatura em **{cidade.title()}** é de **{temp}°C** e o clima está **{clima}**.")

                # ===== Umidade =====
                st.subheader("💧 Umidade do Ar")
                st.success(f"A umidade do ar em **{cidade.title()}** é de **{umidade}%**.")

                # ===== Sugestão de roupa =====
                st.subheader("👕 Sugestão de Roupa")
                if temp < 15:
                    sugest = "🧥 Está bem frio — use um casaco pesado e, se possível, cachecol e luvas!"
                elif 15 <= temp <= 25:
                    sugest = "👕 Temperatura amena — roupas leves com um agasalho à mão."
                else:
                    sugest = "🩳 Está quente — prefira roupas leves e se hidrate bastante!"

                if "chuva" in weather_desc:
                    sugest += " ☔ E não esqueça o guarda-chuva!"

                st.info(sugest)

                # ===== Mensagem final =====
                mensagens_positivas = [
                    "🌈 Acredite em você hoje — cada passo importa!",
                    "🌞 Sorria, o dia está só começando!",
                    "🌻 Que seu dia seja leve e cheio de boas surpresas!",
                    "💪 Confie no seu potencial e vá além!",
                    "✨ Hoje é um ótimo dia para ser feliz!",
                    "🌸 Respire fundo — coisas boas estão vindo!",
                    "🔥 Você é mais forte do que imagina!",
                    "☀️ Espalhe boas energias por onde passar!",
                    "🌼 Lembre-se: cada novo dia é uma nova chance!",
                    "💫 Continue brilhando, o mundo precisa da sua luz!"
                ]

                frase = random.choice(mensagens_positivas)

                st.markdown("---")
                st.markdown(
                    f"🌞 **Tenha um dia incrível, {nome.split()[0].title()}!**\n\n"
                    f"{frase}"
                )

            else:
                st.error("❌ Não foi possível encontrar a cidade. Verifique o nome e tente novamente.")
        except Exception as e:
            st.error(f"Ocorreu um erro ao consultar o clima: {e}")
    else:
        st.warning("Por favor, verifique se a cidade e a chave da API foram configuradas corretamente.")

else:
    st.info("Aguardando seu nome... 😊")

