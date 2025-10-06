import streamlit as st

st.write("Alô mundo")
st.title('saudação')
nome = st.text_input("Digite o seu nome")
if nome:
  st.write(nome.upper())
Responda = st.text_input ("Alô mundo", "nome")
