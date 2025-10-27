import streamlit as st
import plotly.express as px

st.title("📘 Simulador de Rescisão Trabalhista")
st.caption("Projeto de LegalTech (Direito do Trabalho) com Python e Streamlit")

# =============================
# 🔹 ENTRADAS DO USUÁRIO
# =============================
st.header("1️⃣ Dados do contrato")

salario_mensal = st.number_input("💰 Salário Mensal (R$):", min_value=0.0, value=2000.00, step=100.0)
meses_trabalhados = st.number_input("📅 Meses Trabalhados:", min_value=0, max_value=12, value=9)
anos_servico = st.number_input("⏳ Anos de Serviço:", min_value=0, max_value=30, value=3)

st.divider()

# =============================
# 🔹 13º SALÁRIO PROPORCIONAL
# =============================
st.header("2️⃣ 13º Salário Proporcional")

decimo_terceiro = (salario_mensal / 12) * meses_trabalhados
st.markdown(f"""
**Fórmula:** (Salário ÷ 12) × Meses Trabalhados  
**Cálculo:** ({salario_mensal:.2f} ÷ 12) × {meses_trabalhados} = R$ {decimo_terceiro:,.2f}
""")

# =============================
# 🔹 FÉRIAS PROPORCIONAIS + 1/3
# =============================
st.header("3️⃣ Férias Proporcionais + 1/3 Constitucional")

ferias_proporcionais = (salario_mensal / 12) * meses_trabalhados
terco_constitucional = ferias_proporcionais / 3
total_ferias = ferias_proporcionais + terco_constitucional

st.markdown(f"""
**Fórmula das Férias:** (Salário ÷ 12) × Meses Trabalhados  
**Cálculo:** ({salario_mensal:.2f} ÷ 12) × {meses_trabalhados} = R$ {ferias_proporcionais:,.2f}  

**Fórmula do 1/3 Constitucional:** Férias ÷ 3  
**Cálculo:** {ferias_proporcionais:,.2f} ÷ 3 = R$ {terco_constitucional:,.2f}  

**Total:** R$ {total_ferias:,.2f}
""")

st.info("""
🔹 **1/3 Constitucional:** direito previsto no art. 7º, XVII, da Constituição Federal.
Garante que o trabalhador receba um adicional equivalente a 1/3 sobre o valor das férias.
""")

# =============================
# 🔹 AVISO PRÉVIO INDENIZADO
# =============================
st.header("4️⃣ Aviso Prévio Indenizado")

dias_aviso = 30 + (3 * anos_servico)
if dias_aviso > 90:
    dias_aviso = 90
aviso_prev = (salario_mensal / 30) * dias_aviso

st.markdown(f"""
**Fórmula:** (Salário ÷ 30) × Dias de Aviso  
**Cálculo:** ({salario_mensal:.2f} ÷ 30) × {dias_aviso} = R$ {aviso_prev:,.2f}  
""")

st.info("""
🔹 Base legal: Lei nº 12.506/2011 — o aviso prévio é de **30 dias**,
acrescido de **3 dias por ano trabalhado**, limitado a **90 dias**.
""")

# =============================
# 🔹 FGTS + MULTA 40%
# =============================
st.header("5️⃣ FGTS e Multa de 40%")

fgts = salario_mensal * 0.08 * meses_trabalhados
multa_fgts = fgts * 0.40

st.markdown(f"""
**FGTS:** Salário × 8% × Meses Trabalhados  
**Cálculo:** {salario_mensal:.2f} × 0.08 × {meses_trabalhados} = R$ {fgts:,.2f}  

**Multa de 40%:** FGTS × 0.40  
**Cálculo:** {fgts:,.2f} × 0.40 = R$ {multa_fgts:,.2f}
""")

# =============================
# 🔹 INSS (PROGRESSIVO 2025)
# =============================
st.header("6️⃣ INSS (Cálculo Progressivo – 2025)")

base_inss = decimo_terceiro + ferias_proporcionais + aviso_prev

faixas_inss = [
    (1412.00, 0.075),
    (2666.68, 0.09),
    (4000.03, 0.12),
    (7786.02, 0.14)
]

restante = base_inss
valor_inss = 0.0
limites = [1412.00, 2666.68, 4000.03, 7786.02]
previo = 0.0

for limite, aliquota in faixas_inss:
    if restante > limite - previo:
        valor_inss += (limite - previo) * aliquota
        restante -= (limite - previo)
        previo = limite
    else:
        valor_inss += restante * aliquota
        break

st.markdown(f"""
**Base de cálculo:** R$ {base_inss:,.2f}  
**Valor do INSS:** R$ {valor_inss:,.2f}
""")

# =============================
# 🔹 IRRF (2025)
# =============================
st.header("7️⃣ IRRF (Cálculo 2025)")

base_ir = base_inss - valor_inss
if base_ir <= 2259.20:
    aliquota_ir = 0
    deducao_ir = 0
elif base_ir <= 2826.65:
    aliquota_ir = 0.075
    deducao_ir = 169.44
elif base_ir <= 3751.05:
    aliquota_ir = 0.15
    deducao_ir = 381.44
elif base_ir <= 4664.68:
    aliquota_ir = 0.225
    deducao_ir = 662.77
else:
    aliquota_ir = 0.275
    deducao_ir = 896.00

valor_ir = (base_ir * aliquota_ir) - deducao_ir
if valor_ir < 0:
    valor_ir = 0

st.markdown(f"""
**Base após INSS:** R$ {base_ir:,.2f}  
**Alíquota aplicada:** {aliquota_ir*100:.1f}%  
**Dedução:** R$ {deducao_ir:,.2f}  
**Valor do IRRF:** R$ {valor_ir:,.2f}
""")

# =============================
# 🔹 TOTAIS
# =============================
st.header("8️⃣ Totais")

total_bruto = decimo_terceiro + total_ferias + aviso_prev + fgts + multa_fgts
total_descontos = valor_inss + valor_ir
total_liquido = total_bruto - total_descontos

st.markdown(f"""
**Total Bruto (todas as verbas):** R$ {total_bruto:,.2f}  
**Descontos (INSS + IRRF):** R$ {total_descontos:,.2f}  
**💰 Valor Líquido a Receber:** R$ {total_liquido:,.2f}
""")

# =============================
# 🔹 GRÁFICO DE PIZZA
# =============================
st.header("9️⃣ Distribuição dos Valores")

dados = {
    "Verba": ["13º Salário", "Férias + 1/3", "Aviso Prévio", "FGTS", "Multa FGTS", "INSS", "IRRF"],
    "Valor": [decimo_terceiro, total_ferias, aviso_prev, fgts, multa_fgts, -valor_inss, -valor_ir]
}

fig = px.pie(dados, values="Valor", names="Verba", title="Distribuição das Verbas e Descontos na Rescisão")
st.plotly_chart(fig)

# =============================
# 🔹 FONTES E REFERÊNCIAS
# =============================
st.header("📚 Fontes e Base Legal")
st.markdown("""
- **Constituição Federal** – art. 7º, incisos XVII e XXI  
- **CLT (Consolidação das Leis do Trabalho)** – arts. 487, 478 e 479  
- **Lei nº 12.506/2011** – Aviso Prévio proporcional  
- **Lei nº 8.036/1990** – FGTS  
- **Lei nº 8.212/1991** – INSS  
- **Lei nº 9.250/1995** – IRRF  
- **Tabelas de INSS e IRRF 2025 (Receita Federal)**
""")
