import streamlit as st

st.write("Alô mundo")
st.title('saudação')
nome = st.texto_input('Digite o seu nome:')
if nome:
  st.write(nome.upper())
