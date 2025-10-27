import streamlit as st
from datetime import date
from dateutil.relativedelta import relativedelta
import matplotlib.pyplot as plt
import pandas as pd

# --- 1. CONFIGURAÇÃO DA PÁGINA ---

st.set_page_config(
    page_title="Calculadora Rescisória Completa",
    page_icon="👷",
    layout="centered"
)

# --- 2. FUNÇÃO DE CÁLCULO (Lógica Trabalhista) ---

# Função para calcular meses proporcionais
def calcular_meses_proporcionais(admissao, demissao):
    """Calcula os meses proporcionais (com a regra dos 15 dias)."""
    if demissao <= admissao:
        return 0
        
    diferenca = relativedelta(demissao, admissao)
    total_meses = diferenca.years * 12 + diferenca.months
    
    if diferenca.days >= 15:
        total_meses += 1
        
    return total_meses

# Função para calcular o Aviso Prévio
def calcular_aviso_previo(admissao, demissao, salario_base):
    """Calcula o aviso prévio proporcional ao tempo de serviço."""
    diferenca = relativedelta(demissao, admissao)
    anos_trabalhados = diferenca.years
    dias_aviso_previo = 30 + anos_trabalhados * 3  # 30 dias + 3 dias por ano de serviço
    valor_aviso_previo = (salario_base / 30) * dias_aviso_previo  # Aviso prévio proporcional
    return valor_aviso_previo

# Função para calcular o FGTS
def calcular_fgts(salario_base, meses_trabalhados):
    """Calcula o valor do FGTS a ser pago."""
    return salario_base * 0.08 * meses_trabalhados

# Função para calcular a Multa do FGTS
def calcular_multa_fgts(fgts):
    """Calcula a multa de 40% sobre o saldo do FGTS."""
    return fgts * 0.40

# Função para calcular o INSS
def calcular_inss(valor_bruto):
    """Calcula o INSS devido sobre o valor bruto."""
    if valor_bruto <= 1302.00:
        return valor_bruto * 0.075
    elif valor_bruto <= 2571.29:
        return valor_bruto * 0.09
    elif valor_bruto <= 3856.94:
        return valor_bruto * 0.12
    elif valor_bruto <= 7507.49:
        return valor_bruto * 0.14
    else:
        return 0  # Limite máximo do INSS

# Função para calcular o Imposto de Renda (IR)
def calcular_ir(valor_bruto):
    """Calcula o Imposto de Renda sobre o valor bruto."""
    if valor_bruto <= 1903.98:
        return 0
    elif valor_bruto <= 2826.65:
        return valor_bruto * 0.075 - 142.80
    elif valor_bruto <= 3751.05:
        return valor_bruto * 0.15 - 354.80
    elif valor_bruto <= 4664.68:
        return valor_bruto * 0.225 - 636.13
    else:
        return valor_bruto * 0.275 - 869.36

# --- 3. INTERFACE STREAMLIT ---

st.title("👷 Calculadora de Rescisão Completa")
st.markdown("### Férias, 13º, Aviso Prévio, FGTS, Multa FGTS, IR e INSS (Direito do Trabalho)")
st.caption("Insira os dados do contrato para calcular as verbas rescisórias mais comuns de forma completa.")

st.markdown("---")

# 3.1. Entrada de Dados
salario_base = st.number_input(
    "1. Salário Mensal Bruto (R$):",
    min_value=0.01,
    value=2000.00,
    step=100.00,
    format="%.2f"
)

col_adm, col_dem = st.columns(2)

with col_adm:
    data_admissao = st.date_input(
        "2. Data de Admissão (Início do Contrato):",
        value=date(2023, 1, 1),
    )

with col_dem:
    data_demissao = st.date_input(
        "3. Data de Demissão (Fim do Contrato):",
        value=date.today(),
        min_value=data_admissao # Garante que a demissão seja após a admissão
    )

st.markdown("---")

# --- 4. CÁLCULO E EXIBIÇÃO ---

if st.button("Calcular Verbas Rescisórias", type="primary"):
    
    meses_trabalhados = calcular_meses_proporcionais(data_admissao, data_demissao)
    
    if meses_trabalhados <= 0:
        st.error("Verifique as datas de Admissão e Demissão. O cálculo não é possível.")
    else:
        # Cálculos das verbas rescisórias
        valor_13_proporcional = (salario_base / 12) * meses_trabalhados
        valor_ferias_prop_base = (salario_base / 12) * meses_trabalhados
        valor_terco_constitucional = valor_ferias_prop_base / 3
        valor_ferias_total = valor_ferias_prop_base + valor_terco_constitucional
        valor_aviso_previo = calcular_aviso_previo(data_admissao, data_demissao, salario_base)
        fgts = calcular_fgts(salario_base, meses_trabalhados)
        multa_fgts = calcular_multa_fgts(fgts)
        inss = calcular_inss(valor_13_proporcional + valor_ferias_total + valor_aviso_previo)
        ir = calcular_ir(valor_13_proporcional + valor_ferias_total + valor_aviso_previo)

        # Total de verbas (simples)
        total_bruto = valor_13_proporcional + valor_ferias_total + valor_aviso_previo + fgts + multa_fgts
        total_devido = total_bruto - inss - ir

        # --- EXIBIÇÃO DOS RESULTADOS (Métricas Essenciais) ---

        st.subheader(f"Resultado Completo (Meses Contados: {meses_trabalhados})")
        st.success(f"### TOTAL ESTIMADO DEVIDO: R$ {total_devido:,.2f}")
        
        # Passo a passo do cálculo:
        st.markdown("### Passo a Passo do Cálculo:")
        st.write(f"1. **13º Salário Proporcional**: R$ {valor_13_proporcional:,.2f}")
        st.write(f"2. **Férias Proporcionais (+ 1/3)**: R$ {valor_ferias_total:,.2f} (1/3 Adicional: R$ {valor_terco_constitucional:,.2f})")
        st.write(f"3. **Aviso Prévio**: R$ {valor_aviso_previo:,.2f}")
        st.write(f"4. **FGTS**: R$ {fgts:,.2f}")
        st.write(f"5. **Multa do FGTS (40%)**: R$ {multa_fgts:,.2f}")
        st.write(f"6. **INSS**: R$ {inss:,.2f}")
        st.write(f"7. **Imposto de Renda (IR)**: R$ {ir:,.2f}")
        st.write(f"**Total Bruto (sem deduções)**: R$ {total_bruto:,.2f}")
        st.write(f"**Total Devido (com deduções)**: R$ {total_devido:,.2f}")

        # --- Gráfico de Barras com todas as verbas ---
        def plot_grafico_verbas_rescisorias(valor_13, valor_ferias, valor_terco, aviso, fgts, multa, inss, ir):
            categorias = ['13º Salário', 'Férias Proporcionais', '1/3 Adicional', 'Aviso Prévio', 'FGTS', 'Multa FGTS', 'INSS', 'IR']
            valores = [valor_13, valor_ferias, valor_terco, aviso, fgts, multa, inss, ir]
            
            plt.figure(figsize=(10, 6))
            plt.bar(categorias, valores, color=['blue', 'green', 'orange', 'red', 'purple', 'cyan', 'brown', 'pink'])
            plt.title('Distribuição das Verbas Rescisórias', fontsize=14)
            plt.xlabel('Categorias de Verbas', fontsize=12)
            plt.ylabel('Valor (R$)', fontsize=12)
            plt.xticks(rotation=45)
            st.pyplot(plt)

        plot_grafico_verbas_rescisorias(valor_13_proporcional, valor_ferias_total, valor_terco_constitucional, valor_aviso_previo, fgts, multa_fgts, inss, ir)

        # --- Gráfico de Pizza (Percentual de cada parte do total) ---
        def plot_grafico_pizza(valor_13, valor_ferias, valor_terco, aviso, fgts, multa, inss, ir, total):
            categorias = ['13º Salário', 'Férias Proporcionais', '1/3 Adicional', 'Aviso Prévio', 'FGTS', 'Multa FGTS', 'INSS', 'IR']
            valores = [valor_13, valor_ferias, valor_terco, aviso, fgts, multa, inss, ir]
            porcentagens = [v / total * 100 for v in valores]
            
            plt.figure(figsize=(8, 8))
            plt.pie(porcentagens, labels=categorias, autopct='%1.1f%%', startangle=90, colors=['blue', 'green', 'orange', 'red', 'purple', 'cyan', 'brown', 'pink'])
            plt.title('Distribuição Percentual das Verbas Rescisórias', fontsize=14)
            st.pyplot(plt)

        plot_grafico_pizza(valor_13_proporcional, valor_ferias_total, valor_terco_constitucional, valor_aviso_previo, fgts, multa_fgts, inss, ir, total_devido)

        st.markdown("---")
        st.info("⚠️ **Atenção:** Este é um cálculo simplificado. Considere as variações conforme o caso específico.")

st.caption("Projeto de LegalTech (Direito do Trabalho) com Python e Streamlit")
