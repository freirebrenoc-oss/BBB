import streamlit as st
from datetime import date
from dateutil.relativedelta import relativedelta
import pandas as pd
import altair as alt

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Calculadora Rescisória Simplificada (CLT)",
    page_icon="⚖️",
    layout="wide"
)

# --- 2. TABELAS DE IMPOSTOS ---

def get_inss_aliquota_e_deducao(salario_base):
    faixas = [
        (1518.00, 0.075, 0.00),
        (2793.88, 0.09, 22.77),
        (4190.83, 0.12, 106.59),
        (8157.41, 0.14, 190.40)
    ]
    if salario_base <= 0: return 0.0
    base_calculo = min(salario_base, faixas[-1][0])
    
    for teto, aliquota, deducao in reversed(faixas):
        if base_calculo > teto:
            return (base_calculo * aliquota) - deducao
    return base_calculo * faixas[0][1]


def get_irrf_aliquota_e_deducao(base_ir):
    faixas = [
        (2428.80, 0.00, 0.00),
        (2826.65, 0.075, 182.16),
        (3751.05, 0.15, 394.16),
        (4664.68, 0.225, 675.49),
        (999999.00, 0.275, 908.73)
    ]
    if base_ir <= 0: return 0.0
        
    for teto, aliquota, deducao in faixas:
        if base_ir <= teto:
            return (base_ir * aliquota) - deducao
    return (base_ir * faixas[-1][1]) - faixas[-1][2]

# --- 3. FUNÇÕES DE CÁLCULO ---

def calcular_meses_proporcionais(admissao, demissao):
    if demissao <= admissao:
        return 0
        
    diferenca = relativedelta(demissao.replace(day=1), admissao.replace(day=1))
    total_meses = diferenca.years * 12 + diferenca.months + 1 

    if demissao.day < 15 and diferenca.months > 0:
         total_meses -= 1
         
    return total_meses, total_meses 


def calcular_aviso_previo_indenizado(admissao, demissao, salario_base):
    tempo_servico = relativedelta(demissao, admissao)
    anos_trabalhados = tempo_servico.years
    
    dias_ap = 30 + min(anos_trabalhados * 3, 60)
    valor_dia = salario_base / 30.0
    valor_ap = valor_dia * dias_ap
    return valor_ap, dias_ap


def calcular_saldo_salario(salario_base, dias_trabalhados_no_mes):
    valor_dia = salario_base / 30.0
    saldo = valor_dia * dias_trabalhados_no_mes
    return saldo

# --- 4. INTERFACE STREAMLIT ---

st.title("⚖️ Calculadora de Rescisão Trabalhista Simplificada (CLT)")
st.caption("Simulação para Demissão Sem Justa Causa (Iniciativa do Empregador)")

st.markdown("---")

st.subheader("1. Dados Contratuais e Financeiros")

col1, col2 = st.columns(2)
with col1:
    salario_base = st.number_input("Salário Mensal Bruto (R$):", min_value=0.01, value=3000.00, step=100.00, format="%.2f")
    saldo_fgts_base = st.number_input("Saldo do FGTS (R$):", min_value=0.00, value=8000.00, step=100.00, format="%.2f")

with col2:
    data_admissao = st.date_input("Data de Admissão:", value=date(2023, 1, 1))
    data_demissao = st.date_input("Data de Demissão (Efetiva):", value=date.today(), min_value=data_admissao)
    dias_trabalhados = st.number_input("Dias Trabalhados no Último Mês (0 a 30):", min_value=0, max_value=31, value=20, step=1)

st.markdown("---")

# --- 5. CÁLCULOS E RESULTADOS ---

if st.button("Calcular Verbas Rescisórias", type="primary"):
    valor_saldo_salario = calcular_saldo_salario(salario_base, dias_trabalhados)
    meses_13_prop, meses_ferias_prop = calcular_meses_proporcionais(data_admissao, data_demissao)

    valor_13_proporcional = (salario_base / 12) * meses_13_prop

    # Férias proporcionais fixas (30 dias / 12 avos)
    valor_ferias_prop_base = (salario_base / 12) * meses_ferias_prop
    valor_terco_prop = valor_ferias_prop_base / 3
    valor_ferias_prop_total = valor_ferias_prop_base + valor_terco_prop

    valor_ap, dias_ap = calcular_aviso_previo_indenizado(data_admissao, data_demissao, salario_base)
    valor_multa_fgts = saldo_fgts_base * 0.40

    # Base tributável
    base_tributavel = valor_saldo_salario + valor_ap
    inss_principal = get_inss_aliquota_e_deducao(base_tributavel)
    inss_13 = get_inss_aliquota_e_deducao(valor_13_proporcional)

    base_irrf = base_tributavel - inss_principal
    irrf_principal = get_irrf_aliquota_e_deducao(base_irrf)
    total_descontos = inss_principal + irrf_principal + inss_13 

    verbas_brutas_diretas = valor_saldo_salario + valor_ap + valor_13_proporcional + valor_ferias_prop_total
    verbas_pagas_liquidas = verbas_brutas_diretas - total_descontos
    total_liquido_simulado = verbas_pagas_liquidas + saldo_fgts_base + valor_multa_fgts

    # --- EXIBIÇÃO ---
    st.subheader("✅ Resumo dos Cálculos")
    col_liq, col_bruto, col_desc = st.columns(3)
    col_bruto.metric("💰 Total Bruto", f"R$ {verbas_brutas_diretas:,.2f}")
    col_desc.metric("✂️ Descontos (INSS/IRRF)", f"R$ {total_descontos:,.2f}", delta_color="inverse")
    col_liq.metric("💵 Total Líquido", f"R$ {verbas_pagas_liquidas:,.2f}")

    st.success(f"## ➕ Total com FGTS + Multa: R$ {total_liquido_simulado:,.2f}")

    st.markdown("---")
    st.subheader("📊 Detalhamento de Valores")

    df_verbas = pd.DataFrame({
        'Verba': ['Saldo de Salário', '13º Salário Prop.', 'Férias Proporcionais (+1/3)', 'Aviso Prévio', 'Multa FGTS (40%)'],
        'Valor Bruto (R$)': [valor_saldo_salario, valor_13_proporcional, valor_ferias_prop_total, valor_ap, valor_multa_fgts],
        'Natureza': ['Tributável', 'Tributável', 'Isenta', 'Tributável', 'Isenta']
    })

    df_descontos = pd.DataFrame({
        'Desconto': ['INSS (Total)', 'IRRF (Principal)'],
        'Valor (R$)': [inss_principal + inss_13, irrf_principal],
        'Base': ['SS, AP e 13º', 'SS e AP (Após INSS)']
    })

    col_tabela, col_grafico = st.columns([1.5, 1])
    with col_tabela:
        st.markdown("#### Tabela de Proventos e Descontos")
        st.dataframe(df_verbas.style.format({'Valor Bruto (R$)': 'R$ {:,.2f}'}), use_container_width=True, hide_index=True)
        st.dataframe(df_descontos.style.format({'Valor (R$)': 'R$ {:,.2f}'}), use_container_width=True, hide_index=True)

    with col_grafico:
        st.markdown("#### Composição das Verbas Brutas")
        df_pie = pd.DataFrame({
            'Verba': ['Saldo Salário', '13º Prop.', 'Férias Prop.', 'Aviso Prévio'],
            'Valor': [valor_saldo_salario, valor_13_proporcional, valor_ferias_prop_total, valor_ap]
        })
        chart_pie = alt.Chart(df_pie).mark_arc(outerRadius=120).encode(
            theta=alt.Theta(field="Valor", type="quantitative"),
            color=alt.Color(field="Verba", type="nominal"),
            tooltip=['Verba', alt.Tooltip('Valor', format='$,.2f')]
        ).properties(title='Verbas Pagas Diretamente')
        st.altair_chart(chart_pie, use_container_width=True)

    st.markdown("---")
    st.info("⚠️ Simulação baseada na CLT. Convenções coletivas e decisões judiciais podem alterar valores.")
