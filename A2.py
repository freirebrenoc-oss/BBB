import streamlit as st
from datetime import date
from dateutil.relativedelta import relativedelta # Adiciona esta biblioteca para cálculo de meses

# --- 1. CONFIGURAÇÃO DA PÁGINA ---

st.set_page_config(
    page_title="Calculadora Rescisória Básica",
    page_icon="👷",
    layout="centered"
)

# --- 2. FUNÇÃO DE CÁLCULO (Lógica Trabalhista) ---

# Usaremos esta função simples para calcular meses de trabalho
def calcular_meses_proporcionais(admissao, demissao):
    """Calcula os meses proporcionais (com a regra dos 15 dias)."""
    
    # Se a demissão for antes da admissão (erro do usuário)
    if demissao <= admissao:
        return 0
        
    # Calcula a diferença exata entre datas
    diferenca = relativedelta(demissao, admissao)
    
    # Total de meses exatos (anos * 12 + meses)
    total_meses = diferenca.years * 12 + diferenca.months
    
    # Regra dos 15 dias (se o último mês trabalhado tiver 15 dias ou mais, conta como mês cheio)
    # Aqui, simplificamos contando o mês de demissão se os dias forem >= 15
    if diferenca.days >= 15:
        total_meses += 1
        
    return total_meses


# --- 3. INTERFACE STREAMLIT ---

st.title("👷 Calculadora de Rescisão Básica")
st.markdown("### Férias e 13º Proporcionais (Direito do Trabalho)")
st.caption("Insira os dados do contrato para calcular as verbas rescisórias mais comuns de forma simplificada.")

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
        # Lógica de Cálculo:
        # Valor Proporcional = Salário / 12 * Meses Trabalhados
        
        # 4.1. 13º Salário Proporcional
        valor_13_proporcional = (salario_base / 12) * meses_trabalhados
        
        # 4.2. Férias Proporcionais
        # As férias são pagas com acréscimo de 1/3
        valor_ferias_prop_base = (salario_base / 12) * meses_trabalhados
        valor_terco_constitucional = valor_ferias_prop_base / 3
        valor_ferias_total = valor_ferias_prop_base + valor_terco_constitucional
        
        # Total de verbas (simples)
        total_devido = valor_13_proporcional + valor_ferias_total

        # --- EXIBIÇÃO DOS RESULTADOS (Métricas Essenciais) ---
        
        st.subheader(f"Resultado Simplificado (Meses Contados: {meses_trabalhados})")
        st.success(f"### TOTAL ESTIMADO DEVIDO: R$ {total_devido:,.2f}")
        
        col_13, col_ferias = st.columns(2)
        
        col_13.metric(
            "13º Salário Proporcional (Bruto)", 
            f"R$ {valor_13_proporcional:,.2f}"
        )
        
        col_ferias.metric(
            "Férias Proporcionais (+ 1/3)", 
            f"R$ {valor_ferias_total:,.2f}",
            delta=f"1/3 Adicional: R$ {valor_terco_constitucional:,.2f}",
            delta_color="normal"
        )
        
        st.markdown("---")
        st.info("⚠️ **Atenção:** Este é um cálculo simplificado. Não inclui aviso prévio, FGTS, multas, IR ou INSS. Utilize apenas para estimativas iniciais.")

st.caption("Projeto de LegalTech (Direito do Trabalho) com Python e Streaml
