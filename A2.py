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
    if demissao.day >= 15 and diff.months < 12: # Adicionando lógica para evitar dupla contagem em meses
         meses += 1
    return meses

def calcular_aviso_previo(admissao, demissao, salario, motivo):
    """Calcula o aviso prévio proporcional (Lei 12.506/2011)."""
    if motivo != "sem justa causa":
        return 0.0, 0
    
    anos = relativedelta(demissao, admissao).years
    dias = 30 + anos * 3
    if dias > 90:
        dias = 90
        
    valor = (salario / 30) * dias
    return valor, dias

def calcular_fgts(remuneracao):
    """FGTS é 8% sobre a remuneração considerada (simplificação)."""
    return remuneracao * 0.08

def calcular_multa_fgts(fgts):
    """Multa de 40% sobre o FGTS total (simplificação)."""
    return fgts * 0.40

def calcular_inss_progressivo(base):
    """Tabela progressiva de 2024."""
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
        imposto = 908.86 
        
    return max(imposto, 0.0)

def calcular_irrf(base, dependentes):
    """Cálculo simplificado de IRRF (Tabela Mensal 2024)."""
    deducao_dependente = dependentes * 189.59
    base -= deducao_dependente

    # Tabela progressiva (Base de Cálculo x Alíquota x Parcela a Deduzir)
    if base <= 2259.20: 
        aliquota, parcela = 0.0, 0.0
    elif base <= 2826.65:
        aliquota, parcela = 0.075, 169.44
    elif base <= 3751.05:
        aliquota, parcela = 0.15, 381.44
    elif base <= 4664.68:
        aliquota, parcela = 0.225, 662.77
    else: # Acima de R$ 4.664,68
        aliquota, parcela = 0.275, 896.00
    
    imposto = base * aliquota - parcela
    
    return max(imposto, 0.0)


# --- 3. INTERFACE STREAMLIT ---
st.title("👷 Calculadora Completa de Rescisão")
st.markdown("### Simulação do cálculo de verbas rescisórias conforme a CLT.")
st.caption("Ferramenta educacional de LegalTech. **Os cálculos são simplificados e não substituem a folha de pagamento oficial.**")

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
    
dias_trabalhados_no_mes = st.number_input("⏳ Dias trabalhados no mês da demissão (saldo de salário):", 
                                          min_value=0, max_value=30, value=demissao.day, 
                                          help="Número de dias trabalhados no mês da demissão.")

st.markdown("---")

# --- BOTÃO DE CÁLCULO ---
if st.button("Calcular Rescisão", type="primary"):

    meses = calcular_meses_proporcionais(admissao, demissao)

    if meses <= 0:
        st.error("⚠️ Datas inválidas. A demissão deve ocorrer após a admissão.")
    else:
        # --- CÁLCULOS PRINCIPAIS ---
        saldo_salario = (salario / 30) * dias_trabalhados_no_mes
        decimo_terceiro = (salario / 12) * meses
        ferias_prop = (salario / 12) * meses
        um_terco = ferias_prop / 3
        ferias_venc_valor = qtd_ferias_vencidas * (salario + (salario/3))
        aviso_valor, aviso_dias = calcular_aviso_previo(admissao, demissao, salario, motivo)
        
        # --- BASES E TRIBUTAÇÃO (CORRIGIDA) ---
        
        # Verbas Isentas de IR e INSS (Férias Indenizadas, 1/3, Aviso Indenizado)
        verbas_isentas = ferias_prop + um_terco + ferias_venc_valor + aviso_valor
        
        # Base de INSS (incide sobre Saldo Salário + 13º. Simplificação: 13º é tributado separadamente no mundo real)
        base_inss = saldo_salario 
        inss_principal = calcular_inss_progressivo(base_inss)
        
        # IRRF incide sobre Saldo Salário e 13º (o 13º tem tributação exclusiva, mas simplificamos aqui para uma base única)
        base_irrf = saldo_salario - inss_principal
        ir = calcular_irrf(base_irrf, dependentes)

        # FGTS e Multa
        # Simplificação: base de FGTS sobre Salário * Meses Proporcionais
        fgts_base_simplificada = salario * meses 
        fgts = calcular_fgts(fgts_base_simplificada) 
        multa = calcular_multa_fgts(fgts)
        
        # --- TOTAIS ---
        proventos_tributaveis = saldo_salario + decimo_terceiro
        
        total_proventos = proventos_tributaveis + verbas_isentas
        total_bruto = total_proventos + fgts + multa
        descontos = inss_principal + ir
        total_liquido = total_bruto - descontos

        # --- EXIBIÇÃO ---
        st.subheader(f"🧾 Resultado Estimado (Tempo de Serviço: {meses} meses)")
        st.success(f"### 💰 Total Líquido Estimado: R$ {total_liquido:,.2f}")
        st.markdown("---")

        st.markdown(f"""
### 📊 Detalhamento do Cálculo

**1. Saldo de Salário ({dias_trabalhados_no_mes} dias)**: **R$ {saldo_salario:,.2f}**
**2. 13º Salário Proporcional ({meses} avos)**: **R$ {decimo_terceiro:,.2f}**
**3. Férias Proporcionais + 1/3**: **R$ {ferias_prop + um_terco:,.2f}**
**4. Férias Vencidas + 1/3 ({qtd_ferias_vencidas} períodos)**: **R$ {ferias_venc_valor:,.2f}**
**5. Aviso Prévio Indenizado ({aviso_dias} dias)**: **R$ {aviso_valor:,.2f}**
**6. FGTS (Estimado)**: **R$ {fgts:,.2f}**
**7. Multa do FGTS (40%)**: **R$ {multa:,.2f}**

---
<p style='font-size: 14px; margin-bottom: 0px;'><strong>8. Desconto INSS</strong> (Base Simp.: R$ {base_inss:,.2f})</p>
<h3 style='color: red; margin-top: 0px;'>- R$ {inss_principal:,.2f}</h3>

<p style='font-size: 14px; margin-bottom: 0px;'><strong>9. Desconto IRRF</strong> (Base Simp.: R$ {base_irrf:,.2f})</p>
<h3 style='color: red; margin-top: 0px;'>- R$ {ir:,.2f}</h3>

---

### 🧮 Totais

- **Proventos Brutos (Base INSS/IRRF + Isentos):** R$ {total_proventos:,.2f}
- **Total de Descontos:** - R$ {descontos:,.2f}
- **FGTS + Multa (a sacar):** R$ {fgts + multa:,.2f}
- **Líquido Estimado:** 💵 **R$ {total_liquido:,.2f}**
""", unsafe_allow_html=True) # Usando HTML para formatar melhor os descontos


        # --- GRÁFICO DE BARRAS (MANTIDO DO SEU CÓDIGO) ---
        st.markdown("---")
        st.subheader("📈 Distribuição das Verbas (Proventos e Descontos)")
        
        categorias_barras = [
            "Saldo Salário", "13º Prop.", "Férias Prop.", "1/3 Férias", "Férias Venc.", "Aviso Prévio", "FGTS + Multa", "INSS", "IRRF"
        ]
        valores_barras = [
            saldo_salario, decimo_terceiro, ferias_prop, um_terco, ferias_venc_valor, aviso_valor, 
            fgts + multa, -inss_principal, -ir # Valores negativos para descontos
        ]
        cores_barras = ['#4CAF50'] * 7 + ['#F44336'] * 2 # Verde para Proventos, Vermelho para Descontos

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

        # Dados para o Gráfico de Pizza (excluindo FGTS/Multa, INSS, IRRF)
        categorias_pizza = {
            "Saldo Salário": saldo_salario,
            "13º Salário Prop.": decimo_terceiro,
            "Férias Prop.": ferias_prop,
            "1/3 Constitucional": um_terco,
            "Férias Vencidas": ferias_venc_valor,
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
            plt.title("Composição dos Proventos Rescisórios (Exclui FGTS e Descontos)", fontsize=14)
            st.pyplot(plt)
        else:
            st.warning("Não há proventos para exibir no Gráfico de Pizza.")
            
        # --- FONTES E OBSERVAÇÕES (ADICIONADO) ---
        st.markdown("---")
        st.subheader("📚 Fontes e Aviso Legal")
        st.info("""
        **Regras de Cálculo e Tabelas Utilizadas:**
        * **Meses Proporcionais:** Regra da CLT (considera-se 1/12 avos para mês com 15 dias ou mais trabalhados).
        * **Aviso Prévio:** Lei nº 12.506/2011 (30 dias + 3 dias por ano completo).
        * **Tributação (SIMPLIFICADA):** Tabelas de INSS e IRRF de **2024**.

        **⚠️ Aviso Legal (Simulação):**
        * Verbas como **Férias** e **Aviso Prévio Indenizado** são legalmente **ISENTAS** de Imposto de Renda. O 13º Salário tem tributação exclusiva.
        * Esta calculadora usa bases **simplificadas** de INSS e IRRF para fornecer uma estimativa.
        * **Consulte um contador ou advogado trabalhista para valores oficiais e completos.**
        """)
        st.caption("📘 Projeto de LegalTech (Direito do Trabalho) — desenvolvido em Python e Streamlit.")
