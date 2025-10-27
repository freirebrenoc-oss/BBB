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
    # Regra dos 15 dias: se o dia de demissão for 15 ou mais, conta o mês
    if demissao.day >= 15:
        meses += 1
    return meses

def calcular_aviso_previo(admissao, demissao, salario, motivo):
    """Calcula o aviso prévio proporcional (Lei 12.506/2011)."""
    anos = relativedelta(demissao, admissao).years
    dias = 30 + anos * 3
    if dias > 90:
        dias = 90
    if motivo == "sem justa causa":
        # Aviso prévio INDENIZADO é integral.
        valor = (salario / 30) * dias
    else:
        valor = 0
    return valor, dias

def calcular_fgts(remuneracao):
    """FGTS é 8% sobre a remuneração considerada."""
    return remuneracao * 0.08

def calcular_multa_fgts(fgts_total_depositado):
    """Multa de 40% sobre o saldo total do FGTS (simplificação)."""
    return fgts_total_depositado * 0.40

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
            
    if base > 7786.02: # Teto do INSS em 2024
        imposto = 908.86 # Teto máximo de desconto
        
    return max(imposto, 0.0)

def calcular_irrf(base, dependentes):
    """Cálculo simplificado de IRRF (Tabela Mensal 2024)."""
    deducao_dependente = dependentes * 189.59
    base -= deducao_dependente # Deduz dependentes da base
    
    # Tabela progressiva (Base de Cálculo x Alíquota x Parcela a Deduzir)
    if base <= 2259.20:
        aliquota, parcela = 0.0, 0.0
    elif base <= 2826.65:
        aliquota, parcela = 0.075, 169.44
    elif base <= 3751.05:
        aliquota, parcela = 0.15, 381.44
    elif base <= 4664.68:
        aliquota, parcela = 0.225, 662.77
    else:
        aliquota, parcela = 0.275, 896.00

    imposto = base * aliquota - parcela
    return max(imposto, 0.0)

# --- 3. INTERFACE STREAMLIT ---
st.title("👷 Calculadora Completa de Rescisão")
st.markdown("### Simulação de verbas rescisórias conforme a CLT.")
st.caption("Ferramenta educacional de LegalTech. **Os cálculos são estimativos.**")

st.markdown("---")

# --- ENTRADAS ---
salario = st.number_input("💵 Salário Mensal Bruto (R$):", min_value=0.01, value=2400.00, step=100.00, format="%.2f")
col1, col2 = st.columns(2)
with col1:
    admissao = st.date_input("📅 Data de Admissão:", value=date(2022, 1, 1))
with col2:
    demissao = st.date_input("📆 Data de Demissão:", value=date.today(), min_value=admissao)

col3, col4 = st.columns(2)
with col3:
    motivo = st.selectbox("⚖️ Motivo da Rescisão:", ["sem justa causa", "por justa causa"])
with col4:
    dias_trabalhados_no_mes = st.number_input("⏳ Dias trabalhados no mês da demissão:", 
                                              min_value=0, max_value=31, value=demissao.day)

dependentes = st.number_input("👨‍👩‍👧 Número de dependentes (IR):", min_value=0, max_value=10, value=0)
ferias_vencidas = st.radio("🏖️ Possui férias vencidas?", ["Não", "Sim"])
if ferias_vencidas == "Sim":
    qtd_ferias_vencidas = st.number_input("Quantos períodos (simples) de férias vencidas?", min_value=1, max_value=5, value=1)
else:
    qtd_ferias_vencidas = 0

st.markdown("---")

# --- BOTÃO DE CÁLCULO ---
if st.button("Calcular Rescisão", type="primary"):

    meses_prop_13_ferias = calcular_meses_proporcionais(admissao, demissao)

    if meses_prop_13_ferias <= 0:
        st.error("⚠️ Datas inválidas. A demissão deve ocorrer após a admissão.")
    else:
        # --- 4. CÁLCULOS DAS VERBAS ---
        saldo_salario = (salario / 30) * dias_trabalhados_no_mes
        decimo_terceiro = (salario / 12) * meses_prop_13_ferias
        ferias_prop = (salario / 12) * meses_prop_13_ferias
        um_terco_prop = ferias_prop / 3
        ferias_venc_valor = qtd_ferias_vencidas * (salario + (salario/3))
        aviso_valor, aviso_dias = calcular_aviso_previo(admissao, demissao, salario, motivo)

        # --- 5. CÁLCULO TRIBUTÁRIO (CORRIGIDO) ---
        
        # 1. Base INSS (Apenas sobre Saldo de Salário. 13º é separado, mas simplificamos.)
        base_inss = saldo_salario 
        inss = calcular_inss_progressivo(base_inss)
        
        # 2. Base IRRF (Apenas sobre Saldo de Salário - INSS. Férias e Aviso são ISENTOS)
        base_irrf = saldo_salario - inss
        ir = calcular_irrf(base_irrf, dependentes)
        
        # 3. IRRF Exclusivo (Simplificação: apenas 13º Salário)
        ir_13 = calcular_irrf(decimo_terceiro - calcular_inss_progressivo(decimo_terceiro), 0) # 13º tem tributação exclusiva e não usa dedução de dependentes
        
        # --- 6. CÁLCULO FGTS E TOTAIS ---
        
        # Simplificação: base de FGTS sobre Salário * Meses Proporcionais
        fgts_base_simplificada = salario * (relativedelta(demissao, admissao).years * 12 + relativedelta(demissao, admissao).months) 
        fgts = calcular_fgts(fgts_base_simplificada) 
        multa = calcular_multa_fgts(fgts)
        
        # Totalização
        proventos = saldo_salario + decimo_terceiro + ferias_prop + um_terco_prop + ferias_venc_valor + aviso_valor
        total_bruto = proventos + fgts + multa
        descontos = inss + ir + ir_13 # Soma todos os descontos
        total_liquido = total_bruto - descontos

        # --- 7. EXIBIÇÃO DO RESULTADO ---
        st.subheader(f"🧾 Resultado Estimado (Tempo de Serviço: {meses_prop_13_ferias} meses)")
        st.success(f"### 💰 Total Líquido Estimado: R$ {total_liquido:,.2f}")
        st.markdown("---")

        st.markdown(f"""
### 📊 Detalhamento do Cálculo

**1. Saldo de Salário ({dias_trabalhados_no_mes} dias)**: **R$ {saldo_salario:,.2f}**
**2. 13º Salário Proporcional ({meses_prop_13_ferias} avos)**: **R$ {decimo_terceiro:,.2f}**
**3. Férias Proporcionais + 1/3**: **R$ {ferias_prop + um_terco_prop:,.2f}**
**4. Férias Vencidas + 1/3 ({qtd_ferias_vencidas} períodos)**: **R$ {ferias_venc_valor:,.2f}**
**5. Aviso Prévio Indenizado ({aviso_dias} dias)**: **R$ {aviso_valor:,.2f}**
**6. FGTS (Estimado)**: **R$ {fgts:,.2f}**
**7. Multa do FGTS (40%)**: **R$ {multa:,.2f}**

---
<p style='font-size: 14px; margin-bottom: 0px;'>**8. Desconto INSS** (Base Salário: R$ {base_inss:,.2f})</p>
<h3 style='color: red; margin-top: 0px;'>- R$ {inss:,.2f}</h3>

<p style='font-size: 14px; margin-bottom: 0px;'>**9. Desconto IRRF** (Salário) (Base: R$ {base_irrf:,.2f})</p>
<h3 style='color: red; margin-top: 0px;'>- R$ {ir:,.2f}</h3>

<p style='font-size: 14px; margin-bottom: 0px;'>**10. Desconto IRRF** (13º Exclusivo)</p>
<h3 style='color: red; margin-top: 0px;'>- R$ {ir_13:,.2f}</h3>


---

### 🧮 Totais

- **Proventos (a receber na Rescisão):** R$ {proventos:,.2f}
- **Total de Descontos:** - R$ {descontos:,.2f}
- **FGTS + Multa (a sacar na Caixa):** R$ {fgts + multa:,.2f}
- **Líquido Estimado:** 💵 **R$ {total_liquido:,.2f}**
""", unsafe_allow_html=True) 

        # --- GRÁFICO DE BARRAS ---
        st.markdown("---")
        st.subheader("📈 Distribuição das Verbas (Proventos e Descontos)")
        
        categorias_barras = [
            "Salário", "13º", "Férias", "Aviso", "FGTS + Multa", "INSS", "IR Salário", "IR 13º"
        ]
        valores_barras = [
            saldo_salario, decimo_terceiro, ferias_prop + um_terco_prop + ferias_venc_valor, aviso_valor, 
            fgts + multa, -inss, -ir, -ir_13 
        ]
        
        # Filtra categorias com valor zero para não poluir o gráfico
        dados_barras = {c: v for c, v in zip(categorias_barras, valores_barras) if v != 0}
        categorias_barras = list(dados_barras.keys())
        valores_barras = list(dados_barras.values())
        cores_barras = ['#4CAF50' if v >= 0 else '#F44336' for v in valores_barras] # Verde/Vermelho

        plt.figure(figsize=(12, 6))
        plt.bar(categorias_barras, valores_barras, color=cores_barras)
        plt.title("Distribuição e Impacto das Verbas Rescisórias")
        plt.ylabel("Valor (R$)")
        plt.xticks(rotation=45, ha='right')
        plt.axhline(0, color='gray', linewidth=0.8)
        st.pyplot(plt)
        
        # --- GRÁFICO DE PIZZA (ADICIONADO) ---
        st.markdown("---")
        st.subheader("🥧 Proporção dos Proventos Brutos")

        # Dados para o Gráfico de Pizza (apenas verbas de RECEBIMENTO)
        categorias_pizza = {
            "Saldo Salário": saldo_salario,
            "13º Salário Prop.": decimo_terceiro,
            "Férias Prop. + 1/3": ferias_prop + um_terco_prop,
            "Férias Vencidas + 1/3": ferias_venc_valor,
            "Aviso Prévio": aviso_valor,
        }
        
        labels_pizza = []
        sizes_pizza = []
        for cat, val in categorias_pizza.items():
            if val > 0:
                labels_pizza.append(cat)
                sizes_pizza.append(val)
        
        if sum(sizes_pizza) > 0:
            plt.figure(figsize=(8, 8))
            plt.pie(sizes_pizza, labels=labels_pizza, autopct='%1.1f%%', startangle=90, wedgeprops={'edgecolor': 'black'})
            plt.title("Composição dos Proventos Rescisórios (Exceto FGTS)", fontsize=14)
            st.pyplot(plt)
        else:
            st.warning("Não há proventos para exibir no Gráfico de Pizza.")
            
        # --- FONTES E OBSERVAÇÕES ---
        st.markdown("---")
        st.subheader("📚 Fontes e Aviso Legal")
        st.info("""
        **Regras de Cálculo e Tabelas Utilizadas (Simplificadas):**
        * **Tributação (SIMPLIFICADA):** Tabelas de INSS e IRRF de **2024** (visto que as de 2025 podem mudar).
        * **Isenções:** Verbas como Férias e Aviso Prévio Indenizado são consideradas **ISENTAS** na base de cálculo do IRRF. O 13º Salário é tributado separadamente.

        **⚠️ Aviso Legal (Simulação):**
        * Este cálculo é **estimativo** e não considera adicionais, horas extras, faltas, nem a Convenção Coletiva da sua categoria.
        * **Consulte um contador ou advogado trabalhista** para valores oficiais e completos.
        """)
        st.caption("📘 Projeto de LegalTech (Direito do Trabalho) — desenvolvido em Python e Streamlit.")
