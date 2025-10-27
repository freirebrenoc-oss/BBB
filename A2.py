import streamlit as st
from datetime import date
from dateutil.relativedelta import relativedelta
import matplotlib.pyplot as plt

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Calculadora de Rescisão Trabalhista",
    page_icon="👷",
    layout="centered"
)

# --- 2. FUNÇÕES AUXILIARES ---
def calcular_meses_proporcionais(admissao, demissao):
    """Calcula os meses proporcionais (com a regra dos 15 dias)."""
    if demissao <= admissao:
        return 0
    diff = relativedelta(demissao, admissao)
    meses = diff.years * 12 + diff.months
    if diff.days >= 15:
        meses += 1
    return meses

def calcular_aviso_previo(admissao, demissao, salario, motivo):
    """Calcula o aviso prévio proporcional (Lei 12.506/2011)."""
    anos = relativedelta(demissao, admissao).years
    dias = 30 + anos * 3
    if dias > 90:
        dias = 90
    if motivo == "sem justa causa":
        valor = (salario / 30) * dias
    else:
        valor = 0
    return valor, dias

def calcular_fgts(remuneracao):
    """FGTS é 8% sobre a remuneração considerada."""
    return remuneracao * 0.08

def calcular_multa_fgts(fgts):
    """Multa de 40% sobre o saldo do FGTS."""
    return fgts * 0.40

def calcular_inss_progressivo(base):
    """Tabela progressiva de 2024 (vigente)."""
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
            break
    return max(imposto, 0.0)

def calcular_irrf(base, dependentes):
    """Cálculo simplificado com deduções por dependente."""
    deducao_dependente = dependentes * 189.59
    base -= deducao_dependente

    if base <= 1903.98:
        aliquota, parcela = 0.0, 0.0
    elif base <= 2826.65:
        aliquota, parcela = 0.075, 142.80
    elif base <= 3751.05:
        aliquota, parcela = 0.15, 354.80
    elif base <= 4664.68:
        aliquota, parcela = 0.225, 636.13
    else:
        aliquota, parcela = 0.275, 869.36

    imposto = base * aliquota - parcela
    return max(imposto, 0.0)

# --- 3. INTERFACE STREAMLIT ---
st.title("👷 Calculadora Completa de Rescisão")
st.markdown("### Cálculo detalhado de férias, 13º, aviso, FGTS, multa, INSS e IRRF")
st.caption("Ferramenta educacional de LegalTech para cálculos trabalhistas com base na CLT.")

st.markdown("---")

# --- ENTRADAS ---
salario = st.number_input("💵 Salário Mensal Bruto (R$):", min_value=0.01, value=2400.00, step=100.00, format="%.2f")

col1, col2 = st.columns(2)
with col1:
    admissao = st.date_input("📅 Data de Admissão:", value=date(2020, 1, 1))
with col2:
    demissao = st.date_input("📆 Data de Demissão:", value=date.today(), min_value=admissao)

motivo = st.selectbox("⚖️ Motivo da Rescisão:", ["sem justa causa", "por justa causa"])
dependentes = st.number_input("👨‍👩‍👧 Número de dependentes (IR):", min_value=0, max_value=10, value=0)

ferias_vencidas = st.radio("🏖️ Possui férias vencidas?", ["Não", "Sim"])
if ferias_vencidas == "Sim":
    qtd_ferias_vencidas = st.number_input("Quantas férias vencidas?", min_value=1, max_value=5, value=1)
else:
    qtd_ferias_vencidas = 0

st.markdown("---")

# --- BOTÃO DE CÁLCULO ---
if st.button("Calcular Rescisão", type="primary"):

    meses = calcular_meses_proporcionais(admissao, demissao)

    if meses <= 0:
        st.error("⚠️ Datas inválidas. A demissão deve ocorrer após a admissão.")
    else:
        # --- CÁLCULOS ---
        decimo_terceiro = (salario / 12) * meses
        ferias_prop = (salario / 12) * meses
        um_terco = ferias_prop / 3
        ferias_total = ferias_prop + um_terco + (qtd_ferias_vencidas * salario)
        aviso_valor, aviso_dias = calcular_aviso_previo(admissao, demissao, salario, motivo)

        # Base tributável (não inclui FGTS nem multa)
        base_tributavel = decimo_terceiro + ferias_total + aviso_valor
        inss = calcular_inss_progressivo(base_tributavel)
        ir = calcular_irrf(base_tributavel, dependentes)

        fgts = calcular_fgts(salario * meses)
        multa = calcular_multa_fgts(fgts)

        total_bruto = decimo_terceiro + ferias_total + aviso_valor + fgts + multa
        descontos = inss + ir
        total_liquido = total_bruto - descontos

        # --- EXIBIÇÃO ---
        st.subheader(f"🧾 Resultado (Tempo de Serviço: {meses} meses)")
        st.success(f"### 💰 Total Líquido Estimado: R$ {total_liquido:,.2f}")
        st.markdown("---")

        st.markdown(f"""
### 📊 Passo a Passo do Cálculo

**1️⃣ 13º Salário Proporcional**  
→ Fórmula: `(Salário / 12) × Meses Trabalhados`  
→ **R$ {decimo_terceiro:,.2f}**

**2️⃣ Férias Proporcionais**  
→ Fórmula: `(Salário / 12) × Meses Trabalhados`  
→ **R$ {ferias_prop:,.2f}**

**3️⃣ 1/3 Constitucional sobre Férias**  
O trabalhador tem direito a **acréscimo de 1/3 sobre o valor das férias**, garantido pelo art. 7º, XVII, da Constituição.  
→ Fórmula: `Férias Proporcionais ÷ 3`  
→ **R$ {um_terco:,.2f}**

**4️⃣ Férias Vencidas**  
→ Quantidade: {qtd_ferias_vencidas}  
→ **R$ {qtd_ferias_vencidas * salario:,.2f}**

**5️⃣ Aviso Prévio**  
→ Dias: **{aviso_dias} dias**  
→ Fórmula: `(Salário / 30) × Dias de Aviso`  
→ **R$ {aviso_valor:,.2f}**

**6️⃣ FGTS (8%)**  
→ Base: Salário × Meses Trabalhados  
→ **R$ {fgts:,.2f}**

**7️⃣ Multa do FGTS (40%)**  
→ Fórmula: `FGTS × 0,40`  
→ **R$ {multa:,.2f}**

**8️⃣ INSS (Progressivo)**  
→ Aplicação da tabela oficial de 2024  
→ **R$ {inss:,.2f}**

**9️⃣ IRRF (após deduções)**  
→ Considerando deduções legais por dependentes  
→ **R$ {ir:,.2f}**

---
### 🧮 Totais

- **Bruto Total:** R$ {total_bruto:,.2f}  
- **Descontos Totais:** R$ {descontos:,.2f}  
- **Líquido Estimado:** 💵 **R$ {total_liquido:,.2f}**
""")

        # --- GRÁFICOS ---
        st.markdown("### 📈 Visualização Gráfica")

        categorias = ["13º", "Férias", "1/3", "Aviso", "FGTS", "Multa FGTS", "INSS", "IRRF"]
        valores = [decimo_terceiro, ferias_prop, um_terco, aviso_valor, fgts, multa, inss, ir]

        fig, ax = plt.subplots(figsize=(8, 6))
        ax.pie(valores, labels=categorias, autopct='%1.1f%%', startangle=90)
        ax.set_title("Distribuição das Verbas e Descontos na Rescisão")
        st.pyplot(fig)

        st.markdown("---")

        st.info("⚠️ Cálculo estimativo com base em regras gerais da CLT e tabelas tributárias vigentes. Consulte um contador ou advogado trabalhista para valores oficiais.")
        st.caption("""
📘 **Fontes Consultadas:**  
- Consolidação das Leis do Trabalho (CLT)  
- Constituição Federal, art. 7º, XVII (1/3 constitucional sobre férias)  
- Lei nº 12.506/2011 (aviso prévio proporcional)  
- Receita Federal do Brasil — Tabelas de INSS e IRRF (2024)  
- Caixa Econômica Federal — Regulamento do FGTS
""")

