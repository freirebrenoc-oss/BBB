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

    # Simplificação: conta o mês de demissão se o dia for 15 ou mais
    # Esta regra se aplica ao mês de início do contrato e ao mês de fim.
    # Assumimos que o mês de início já está contado na diferença (meses).
    if demissao.day >= 15:
         meses += 1
    
    # Ajuste para evitar contar o mês duas vezes se o dia for 15 ou mais
    # e a relativedelta já tiver arredondado (o que não acontece na relativedelta simples).
    
    return meses

def calcular_aviso_previo(admissao, demissao, salario, motivo):
    """Calcula o aviso prévio proporcional (Lei 12.506/2011)."""
    if motivo != "sem justa causa":
        return 0.0, 0
    
    anos = relativedelta(demissao, admissao).years
    
    # 30 dias base + 3 dias por ano completo
    dias = 30 + anos * 3
    
    # Limite de 90 dias
    if dias > 90:
        dias = 90
        
    valor = (salario / 30) * dias
    
    return valor, dias

def calcular_fgts(salario_base, meses_trabalhados):
    """FGTS é 8% sobre a remuneração considerada."""
    # Simulação: Base de cálculo aproximada: Salário Base * Meses Proporcionais
    remuneracao_base_fgts = salario_base * meses_trabalhados
    return remuneracao_base_fgts * 0.08

def calcular_multa_fgts(fgts_total_depositado):
    """Multa de 40% sobre o saldo total do FGTS (aproximado)."""
    return fgts_total_depositado * 0.40

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
            base_anterior = base
            break
            
    if base > 7786.02: # Teto do INSS em 2024 (R$ 908,86)
        imposto = 908.86 
        
    return max(imposto, 0.0)

def calcular_irrf(base, dependentes):
    """Cálculo simplificado de IRRF (Tabela Mensal 2024)."""
    deducao_dependente = dependentes * 189.59
    base_deduzida = base - deducao_dependente

    # Tabela progressiva (Base de Cálculo x Alíquota x Parcela a Deduzir)
    if base_deduzida <= 2259.20: 
        aliquota, parcela = 0.0, 0.0
    elif base_deduzida <= 2826.65:
        aliquota, parcela = 0.075, 169.44
    elif base_deduzida <= 3751.05:
        aliquota, parcela = 0.15, 381.44
    elif base_deduzida <= 4664.68:
        aliquota, parcela = 0.225, 662.77
    else: # Acima de R$ 4.664,68
        aliquota, parcela = 0.275, 896.00
    
    imposto = base_deduzida * aliquota - parcela
    
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
    min_demissao = admissao
    demissao = st.date_input("📆 Data de Demissão (Rescisão):", value=date.today(), min_value=min_demissao)

motivo = st.selectbox("⚖️ Motivo da Rescisão:", ["sem justa causa", "por justa causa"])
dependentes = st.number_input("👨‍👩‍👧 Número de dependentes (IR):", min_value=0, max_value=10, value=0)
ferias_vencidas = st.radio("🏖️ Possui férias vencidas (simples)?", ["Não", "Sim"])
if ferias_vencidas == "Sim":
    qtd_ferias_vencidas = st.number_input("Quantas férias vencidas (períodos)?", min_value=1, max_value=5, value=1)
else:
    qtd_ferias_vencidas = 0

# Saldo de salário (Simplificação: Dias trabalhados no mês da demissão, excluindo o aviso prévio)
dias_trabalhados_no_mes = st.number_input("⏳ Dias trabalhados no mês da demissão (excluindo aviso):", 
                                          min_value=0, max_value=30, value=0, help="Considerar dias até a data da rescisão, se menor que 30.")

st.markdown("---")

# --- BOTÃO DE CÁLCULO ---
if st.button("Calcular Rescisão", type="primary"):

    # CÁLCULOS
    saldo_salario = (salario / 30) * dias_trabalhados_no_mes
    meses_prop = calcular_meses_proporcionais(admissao, demissao)

    if meses_prop < 0:
        st.error("⚠️ Datas inválidas. A demissão deve ocorrer após a admissão.")
    else:
        
        # Verbas Rescisórias (Proventos)
        decimo_terceiro = (salario / 12) * meses_prop
        ferias_prop = (salario / 12) * meses_prop
        um_terco = ferias_prop / 3
        # Férias vencidas: Salário + 1/3 (Não está sendo considerada a dobra legal para férias vencidas não usufruídas)
        ferias_venc_valor = qtd_ferias_vencidas * (salario + (salario/3))
        aviso_valor, aviso_dias = calcular_aviso_previo(admissao, demissao, salario, motivo)

        # FGTS e Multa
        fgts_base_simplificada = salario * meses_prop
        fgts = calcular_fgts(salario, meses_prop)
        multa = calcular_multa_fgts(fgts)

        # Descontos (Tributos)
        # Base correta INSS: Saldo Salário + 13º (Base de 13º separada) + Aviso Prévio Trabalhado.
        # Simplificação: Usaremos Saldo Salário + 13º Prop.
        inss_base_correta_simulada = saldo_salario + decimo_terceiro
        inss = calcular_inss_progressivo(inss_base_correta_simulada) 
        
        # Base de IRRF (Aviso Indenizado e Férias Indenizadas + 1/3 são isentos)
        # Simplificação: Base tributável (saldo + 13º) para demonstração da função.
        base_tributavel = saldo_salario + decimo_terceiro
        ir = calcular_irrf(base_tributavel, dependentes) 

        # Totalização
        total_proventos = saldo_salario + decimo_terceiro + ferias_prop + um_terco + ferias_venc_valor + aviso_valor
        total_bruto = total_proventos + fgts + multa
        descontos = inss + ir
        total_liquido = total_bruto - descontos

        # --- EXIBIÇÃO ---
        st.subheader(f"🧾 Resultado (Tempo de Serviço: {meses_prop} meses)")
        st.success(f"### 💰 Total Líquido Estimado: R$ {total_liquido:,.2f}")
        st.markdown("---")

        # --- PASSO A PASSO MATEMÁTICO DETALHADO (CORRIGIDO) ---
        st.subheader("💡 Passo a Passo Matemático Detalhado")
        st.markdown("O cálculo estima os valores com base nas suas entradas. As bases de cálculo do INSS e IRRF podem variar.")
        
        # Usando notação simples para evitar problemas de renderização de LaTeX complexo em Markdown
        st.markdown(f"""
        1. **Saldo de Salário:** (R$ {salario:,.2f} / 30) x {dias_trabalhados_no_mes} dias = **R$ {saldo_salario:,.2f}**
        2. **13º Salário Prop.:** (R$ {salario:,.2f} / 12) x {meses_prop} meses = **R$ {decimo_terceiro:,.2f}**
        3. **Férias Prop. + 1/3:** [ (R$ {salario:,.2f} / 12) x {meses_prop} meses ] x 1.3333 = **R$ {ferias_prop + um_terco:,.2f}**
        4. **Férias Venc. + 1/3:** (R$ {salario:,.2f} x 1.3333) x {qtd_ferias_vencidas} períodos = **R$ {ferias_venc_valor:,.2f}**
        5. **Aviso Prévio (Indenizado):** (R$ {salario:,.2f} / 30) x {aviso_dias} dias = **R$ {aviso_valor:,.2f}**
        6. **FGTS (Aproximado):** R$ {fgts_base_simplificada:,.2f} x 8% = **R$ {fgts:,.2f}**
        7. **Multa 40% FGTS:** R$ {fgts:,.2f} x 40% = **R$ {multa:,.2f}**

        ---
        
        * **Base de INSS (Simulada):** R$ {inss_base_correta_simulada:,.2f} $\\rightarrow$ **INSS (Progressivo): R$ {inss:,.2f}**
        * **Base de IRRF (Simulada):** R$ {base_tributavel:,.2f} - (Dependentes {dependentes} x R$189.59) = R$ {base_tributavel - dependentes * 189.59:,.2f} $\\rightarrow$ **IRRF: R$ {ir:,.2f}**

        ---

        * **Proventos (Soma 1 a 5):** **R$ {total_proventos:,.2f}**
        * **Total Bruto (Proventos + FGTS/Multa):** **R$ {total_bruto:,.2f}**
        * **Total Líquido:** R$ {total_bruto:,.2f} - R$ {descontos:,.2f} = 💵 **R$ {total_liquido:,.2f}**
        """)
        
        st.markdown("---")


        # --- GRÁFICO DE BARRAS ---
        st.subheader("📈 Distribuição das Verbas Rescisórias (Gráfico de Barras)")
        
        categorias_recebimento = {
            "Saldo de Salário": saldo_salario,
            "13º Prop.": decimo_terceiro,
            "Férias Prop. + 1/3": ferias_prop + um_terco,
            "Férias Vencidas + 1/3": ferias_venc_valor,
            "Aviso Prévio": aviso_valor,
            "FGTS + Multa": fgts + multa,
        }
        
        categorias_desconto = {
            "INSS": inss * (-1),
            "IRRF": ir * (-1),
        }
        
        categorias_barras = list(categorias_recebimento.keys()) + list(categorias_desconto.keys())
        valores_barras = list(categorias_recebimento.values()) + list(categorias_desconto.values())

        cores_barras = ['#4CAF50'] * len(categorias_recebimento) + ['#F44336'] * len(categorias_desconto)
        
        plt.figure(figsize=(12, 6))
        plt.bar(categorias_barras, valores_barras, color=cores_barras)
        plt.title("Distribuição e Impacto das Verbas Rescisórias", fontsize=14)
        plt.ylabel("Valor (R$)", fontsize=12)
        plt.xticks(rotation=45, ha='right', fontsize=10)
        plt.axhline(0, color='gray', linewidth=0.8)
        
        st.pyplot(plt)

        st.markdown("---")

        # --- GRÁFICO DE PIZZA ---
        st.subheader("🥧 Proporção das Verbas de Recebimento (Gráfico de Pizza)")

        labels = []
        sizes = []
        for cat, val in categorias_recebimento.items():
            if val > 0:
                labels.append(cat)
                sizes.append(val)
        
        if sizes:
            plt.figure(figsize=(8, 8))
            plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, wedgeprops={'edgecolor': 'black'})
            plt.title("Composição do Valor Bruto dos Proventos", fontsize=14)
            st.pyplot(plt)
        else:
            st.warning("Não há valores positivos para exibir no Gráfico de Pizza (Verbas de Recebimento).")
            
        st.markdown("---")
        
        # --- FONTES E OBSERVAÇÕES ---
        st.subheader("📚 Fontes e Observações")
        st.info("""
        **Regras de Cálculo e Tabelas Utilizadas:**
        * **Meses Proporcionais (13º e Férias):** Regra da CLT (considera-se 1/12 avos para mês com 15 dias ou mais trabalhados).
        * **Aviso Prévio Indenizado:** Lei nº 12.506/2011 (30 dias + 3 dias por ano completo, limitado a 90 dias).
        * **INSS (Simulação):** Tabela Progressiva do INSS de **2024** (Portaria Interministerial MTP/ME Nº 2/2024).
        * **IRRF (Simulação):** Tabela Progressiva Mensal do IRRF de **2024** (MP nº 1.206/2024).
        
        **⚠️ Advertências Legais (Simplificações):**
        * **Aviso Prévio Indenizado** e **Férias Indenizadas + 1/3** são **ISENTOS de Imposto de Renda** (Lei 7.713/88). Esta calculadora simula o IRRF apenas sobre o Saldo de Salário e 13º.
        * O **INSS** não incide sobre Férias (proporcionais e vencidas) e 1/3 Constitucional. A base INSS simulada exclui esses valores.
        * Este é um cálculo **estimativo** e não substitui a orientação de um contador ou advogado trabalhista.
        """)
        st.caption("📘 Projeto de LegalTech (Direito do Trabalho) — desenvolvido em Python e Streamlit.")
