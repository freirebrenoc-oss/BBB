import streamlit as st

# Define o título principal da aplicação
st.title('Aplicativo de Manhã matinal')

# Exibe uma mensagem introdutória
st.write("Bem-vindo! Digite seu nome abaixo para uma saudação.")

# Campo de entrada de texto para o nome do usuário
nome = st.text_input("Digite o seu nome aqui")

# Verifica se o usuário digitou algo
if nome:
    # Cria a mensagem de saudação, transformando o nome para letras MAIÚSCULAS
    # para cumprir o objetivo do seu código original (nome.upper())
    mensagem_final = f"OLÁ, {nome.upper()}! É UM PRAZER TE VER POR AQUI."
    
    # Exibe a mensagem final formatada
    st.success(mensagem_final)
    
    # Você também pode adicionar um texto de suporte, se quiser:
    # st.caption("Sua saudação está pronta!")
else:
    # Mensagem exibida enquanto o campo de nome está vazio
    st.info("Aguardando seu nome...")

# Trazer algum tipo de serviço
    opcao = st.selectbox(
        "Escolha um serviço:",
        ["Selecione...", "Ver temperatura", "Ver umidade do ar", "Ver trânsito", "Sugestão de roupa"])
  
    # Mostra o que foi escolhido
    if opcao != "Selecione...":
        st.info(f"Você escolheu: {opcao}")
else:
    st.info("Aguardando seu serviço...")




