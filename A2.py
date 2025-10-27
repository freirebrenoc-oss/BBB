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

def calcular_meses_proporcionais(admissao, demissao):
    """Calcula os meses proporcionais (com a regra dos 15 dias)."""
    if demissao <= admissao:
        return 0
    diferenca = relativedelta(demissao, admissao)
    total_meses = diferenca.years * 12 + diferenca.months
    if diferenca.days >= 15:
        total_meses += 1
    return total_meses

def calcular_aviso_previo(admissao, demissao, salario_base, motivo_rescisao):
    """Calcula o aviso prévio proporcional ao tempo de serviço (Lei 12.506/2011)."""
    diferenca = relativedelta(demissao, admissao)
    anos_trabalhados = diferenca.years
    dias_aviso_previo = 30 + anos_trabalhados * 3
    if dias_aviso_previo > 90:
        dias_aviso_previo = 90

    if motivo_rescisao == "sem justa causa":
        valor_aviso_previo = (salario_base / 30) * dias_aviso_previo
    else:
        valor_aviso_previo = 0
    return valor_aviso_previo, dias_aviso_previo

def calcular_fgts(salario_base, meses_trabalhados):
    """Calcula o FGTS (8% por mês)."""
    return salario_base * 0.08 * meses_trabalhados

def calcular_multa_fgts(fgts):
    """Calcula a multa de 40% sobre o FGTS."""
    return fgts * 0.40

def calcular_inss_progressivo(base):
    """Cálculo progressivo do INSS."""
    faixas = [
        (1412.00, 0.075),
        (2666.68, 0.09),
        (4000.03, 0.12),
        (7786.02, 0.14)
    ]
    imposto = 0.0
    base_anterior = 0.0
    for limite, aliquota in faixas:
        if base > limite:
            imposto += (limite - base_anterior) * aliquota
            base_anterior = limite
        else:
            imposto += (base - base_anterior) * aliquota
            return max(imposto, 0.0)
    return max(imposto, 0.0)

def calcular_ir_rescisao(base_ir, dependentes):
    """Cálculo progressivo do IRRF sobre base de rescisão."""
    deducao_dependentes = dependentes * 189.59
    base = base_ir - deducao_dependentes

    if base <= 1903.98:
        aliquota = 0.0
        parcela = 0.0
    elif base <= 2826.65:
        aliquota = 0.075
        parcela = 142.80
    elif base <= 3751.05:
        aliquota = 0.15
        parcela = 354.80
    elif base <= 4664.68:
        aliquota = 0.225
        parcela = 636.13
    else:
        aliquota = 0.275
        parcela = 869.36

    imposto = base * aliquota - parcela
    imposto = max(imposto, 0.0)
    return imposto, aliquota * 100, parcela, deducao_dependentes

# --- 3. INTERFACE STREAMLIT ---
st.title("👷 Calculadora de Rescisão Completa")
st.markdown("### Férias, 13º, Aviso Prévio, FGTS, Multa FGTS, IR e INSS (Direito do Trabalho)")
st.caption("Insira os dados do contrato para calcular as verbas rescisórias mais comuns de forma completa.")
st.markdown("---")

salario_base = st.number_input("1. Salário Mensal Bruto (R$):", min_value=0.01, value=2000.00, step=100.00, format="%.2f")

col_adm, col_dem = st.columns(2)
with col_adm:
    data_admissao = st.date_input("2. Data de Admissão:", value=date(2013, 1, 1))
with col_dem:
    data_demissao = st.date_input("3. Data de Demissão:", value=date.today(), min_value=data_admissao)

motivo_rescisao = st.selectbox("4. Motivo da Rescisão:", ["sem justa causa", "por justa causa"])
dependentes = st.number_input("5. Nº de dependentes (IR):", min_value=0, max_value=10, value=0)
ferias_vencidas = st.radio("6. Há férias vencidas?", ("Não", "Sim"))

if ferias_vencidas == "Sim":
    num_ferias_vencidas = st.number_input("Quantas férias vencidas?", min_value=0, max_value=5, value=0)
else:
    num_ferias_vencidas = 0

st.markdown("---")

# --- 4. CÁLCULO E EXIBIÇÃO ---
if st.button("Calcular Verbas Rescisórias", type="primary"):
    meses_trabalhados = calcular_meses_proporcionais(data_admissao, data_demissao)

    if meses_trabalhados <= 0:
        st.error("⚠️ As datas estão incorretas.")
    else:
        valor_13 = (salario_base / 12) * meses_trabalhados
        ferias_base = (salario_base / 12) * meses_trabalhados
        terco = ferias_base / 3
        ferias_total = ferias_base + terco + (num_ferias_vencidas * salario_base)
        aviso, dias_aviso = calcular_aviso_previo(data_admissao, data_demissao, salario_base, motivo_rescisao)
        fgts = calcular_fgts(salario_base, meses_trabalhados)
        multa = calcular_multa_fgts(fgts)

        base_trib = valor_13 + ferias_total + aviso
        inss = calcular_inss_progressivo(base_trib)
        ir, aliq_ir, parcela_ir, deduc = calcular_ir_rescisao(base_trib, dependentes)

        total_bruto = valor_13 + ferias_total + aviso + fgts + multa
        descontos = inss + ir
        total_liquido = total_bruto - descontos

        st.subheader(f"🧾 Resultado Completo (Meses: {meses_trabalhados})")
        st.success(f"### 💰 Total Líquido Estimado: R$ {total_liquido:,.2f}")
        st.markdown("---")

        # EXIBIÇÃO FORMATADA
        st.markdown(f"""
### 🧮 Passo a Passo do Cálculo:

**1. 13º Salário Proporcional**  
Fórmula: `(Salário Mensal / 12) × Meses Trabalhados`  
Valor: **R$ {valor_13:,.2f}**

**2. Férias Proporcionais (+1/3 Constitucional)**  
Fórmula: `(Salário Mensal / 12) × Meses Trabalhados`  
1/3 Adicional: **R$ {terco:,.2f}**  
Total de Férias (+1/3): **R$ {ferias_total:,.2f}**

**3. Aviso Prévio**  
Fórmula: `(Salário Mensal / 30) × Dias`  
Dias Calculados: **{dias_aviso} dias**  
Valor: **R$ {aviso:,.2f}**

**4. FGTS**  
Fórmula: `Salário Mensal × 0.08 × Meses Trabalhados`  
Valor: **R$ {fgts:,.2f}**

**5. Multa do FGTS (40%)**  
Fórmula: `FGTS × 0.40`  
Valor: **R$ {multa:,.2f}**

**6. INSS (Progressivo)**  
Base de cálculo: **R$ {base_trib:,.2f}**  
Valor calculado: **R$ {inss:,.2f}**

**7. Imposto de Renda (IRRF)**  
Base após deduções: **R$ {base_trib - deduc:,.2f}**  
Deduções por dependente (R$ 189,59/unid): **R$ {deduc:,.2f}**  
Alíquota: **{aliq_ir:.1f}%** | Parcela a deduzir: **R$ {parcela_ir:,.2f}**  
Valor do IR: **R$ {ir:,.2f}**

---

### 📊 Totais:
- **Total Bruto (sem deduções):** R$ {total_bruto:,.2f}  
- **Total Descontos (INSS + IR):** R$ {descontos:,.2f}  
- **Total Líquido (com deduções):** R$ {total_liquido:,.2f}
""")

        # --- GRÁFICO DE BARRAS ---
        def plot_grafico_barras():
            categorias = ['13º', 'Férias', '1/3', 'Aviso', 'FGTS', 'Multa', 'INSS', 'IR']
            valores = [valor_13, ferias_base, terco, aviso, fgts, multa, inss, ir]
            plt.figure(figsize=(10, 6))
            plt.bar(categorias, valores)
            plt.title("Distribuição das Verbas Rescisórias", fontsize=14)
            plt.xlabel("Categorias")
            plt.ylabel("Valor (R$)")
            plt.xticks(rotation=45)
            st.pyplot(plt)

        plot_grafico_barras()

        st.markdown("---")
        st.info("⚠️ Cálculo estimado com base em parâmetros padrão. Consulte um contador ou advogado trabalhista para casos reais.")
