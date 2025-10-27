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

# --- 2. FUNÇÕES AUXILIARES (AS FUNÇÕES DE CÁLCULO FORAM MANTIDAS PARA GARANTIR O RESULTADO) ---

def calcular_meses_proporcionais(admissao, demissao):
    """Calcula os meses proporcionais (com a regra dos 15 dias)."""
    if demissao <= admissao:
        return 0
    
    diff = relativedelta(demissao, admissao)
    meses = diff.years * 12 + diff.months

    # Simplificação: conta o mês de demissão se o dia for 15 ou mais
    if demissao.day >= 15:
         meses += 1
    
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
    # Usando a tabela de 2024 como fallback para simulação (valores no código anterior)
    faixas = [
        (1412.00, 0.075),
        (2666.68, 0.09),
        (4000.03, 0.12),
        (7786.02, 0.14)
    ]
    imposto = 0.0
    base_anterior = 0.0
    
    # ... (cálculo omitido por brevidade, mas o INSS é calculado internamente)
    
    # Apenas para garantir o valor do INSS na simulação, usando a lógica do código anterior:
    if base <= 1412.00:
        imposto = base * 0.075
    elif base <= 2666.68:
        imposto = (1412.00 * 0.075) + ((base - 1412.00) * 0.09)
    elif base <= 4000.03:
        imposto = (1412.00 * 0.075) + ((2666.68 - 1412.00) * 0.09) + ((base - 2666.68) * 0.12)
    elif base <= 7786.02:
        imposto = (1412.00 * 0.075) + ((2666.68 - 1412.00) * 0.09) + ((4000.03 - 2666.68) * 0.12) + ((base - 4000.03) * 0.14)
    else:
        imposto = 908.86 # Teto do INSS em 2024
            
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
st.markdown("### Simulação do cálculo de verbas rescisórias conforme a CLT.")
st.caption("Ferramenta educacional de LegalTech. **Os cálculos são simplificados e não substituem a folha de pagamento oficial.**")

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
        ferias_venc_valor = qtd_ferias_vencidas * (salario + (salario/3))
        aviso_valor, aviso_dias = calcular_aviso_previo(admissao, demissao, salario, motivo)

        # FGTS e Multa
        fgts_base_simplificada = salario * meses_prop
        fgts = calcular_fgts(salario, meses_prop)
        multa = calcular_multa_fgts(fgts)

        # Descontos (Tributos)
        inss_base_correta_simulada = saldo_salario + decimo_terceiro # Simplificação
        inss = calcular_inss_progressivo(inss_base_correta_simulada) 
        base_tributavel = saldo_salario + decimo_terceiro # Simplificação
        ir = calcular_irrf(base_tributavel, dependentes) 

        # Totalização
        total_proventos = saldo_salario + decimo_terceiro + ferias_prop + um_terco + ferias_venc_valor + aviso_valor
        total_bruto = total_proventos + fgts + multa
        descontos = inss + ir
        total_liquido = total_bruto - descontos

        # --- EXIBIÇÃO ---
        st.subheader(f"🧾 Resultado Estimado (Tempo de Serviço: {meses_prop} meses)")
        st.success(f"### 💰 Total Líquido Estimado: R$ {total_liquido:,.2f}")
        
        col_res1, col_res2, col_res3 = st.columns(3)
        col_res1.metric("Proventos", f"R$ {total_proventos:,.2f}")
        col_res2.metric("FGTS + Multa", f"R$ {fgts + multa:,.2f}")
        col_res3.metric("Descontos", f"- R$ {descontos:,.2f}")

        st.markdown("---")


        # --- GRÁFICO DE BARRAS ---
        st.subheader("📈 Distribuição das Verbas (Gráfico de Barras)")
        
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
        st.subheader("📚 Observações e Aviso Legal")
        st.warning("""
        **⚠️ Aviso de Simulação:**
        * Este é um cálculo **estimativo**. Os valores de INSS e IRRF utilizam tabelas simplificadas (Base: 2024/2025) e as regras de dedução e incidência real podem ser mais complexas.
        * **Não substitui** o cálculo oficial da folha de pagamento feito por um contador ou o cálculo judicial realizado por um perito.
        * **Aconselha-se sempre a consulta** a um profissional de contabilidade ou a um advogado trabalhista para obter valores exatos e completos.
        """)
        st.caption("📘 Projeto de LegalTech (Direito do Trabalho) — desenvolvido em Python e Streamlit.")
