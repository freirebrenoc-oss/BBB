import streamlit as st
from datetime import date
from dateutil.relativedelta import relativedelta
import pandas as pd
import altair as alt # Para os gráficos

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Calculadora Rescisória Completa",
    page_icon="⚖️",
    layout="wide"
)

# --- 2. TABELAS DE IMPOSTOS (SIMPLIFICADAS) ---
# **AVISO:** Essas tabelas são simplificações e podem ter sido alteradas.
# Use valores atualizados para cálculos oficiais.

# Tabela INSS Progressiva (exemplo com valores de 2025)
def get_inss_aliquota_e_deducao(salario_base):
    # Tabela de faixas progressivas (Salário de Contribuição)
    # Fonte: Exemplo de 2025
    faixas = [
        (1518.00, 0.075, 0.00),      # Até 1.518,00 | Alíquota: 7.5% | Dedução: 0,00
        (2793.88, 0.09, 22.77),      # De 1.518,01 até 2.793,88 | Alíquota: 9% | Dedução: 22,77
        (4190.83, 0.12, 106.59),     # De 2.793,89 até 4.190,83 | Alíquota: 12% | Dedução: 106,59
        (8157.41, 0.14, 190.40)      # De 4.190,84 até 8.157,41 (Teto) | Alíquota: 14% | Dedução: 190,40
    ]
    
    # Aplica o cálculo progressivo
    if salario_base <= 0:
        return 0.0
    
    inss_devido = 0.0
    base_calculo = salario_base
    
    # Se o salário for maior que o teto, a base de cálculo é o teto (8157.41)
    if salario_base > faixas[-1][0]:
        base_calculo = faixas[-1][0]
    
    # Fórmula Simplificada com Parcela a Deduzir (Método mais comum em software)
    for teto, aliquota, deducao in reversed(faixas):
        if base_calculo > teto:
            return (base_calculo * aliquota) - deducao
            
    # Para a primeira faixa, aplica a alíquota de 7.5%
    return base_calculo * faixas[0][1]


# Tabela IRRF (Imposto de Renda Retido na Fonte) Mensal (exemplo de 2025/2026)
def get_irrf_aliquota_e_deducao(base_ir):
    # Base IR: Rendimento Tributável (Salário + AP + SS + 13º 2ª parcela - INSS)
    # Atenção: O 13º e AP não entram na base do IR mensal, mas a base é o total do mês.
    # Para fins de simulação, vamos considerar a base para verbas não isentas.
    
    # Rendimentos isentos: Férias (+ 1/3) e Multa FGTS NÃO são base de IRRF.
    # Base IR: Saldo de Salário + Aviso Prévio (se for o caso) - INSS
    
    # Tabela de faixas (Exemplo pós-maio/2025)
    faixas = [
        (2428.80, 0.00, 0.00),     # Até 2.428,80 | Alíquota: 0% | Dedução: 0,00 (Faixa Isenta)
        (2826.65, 0.075, 182.16),  # De 2.428,81 até 2.826,65 | Alíquota: 7.5% | Dedução: 182,16
        (3751.05, 0.15, 394.16),   # De 2.826,66 até 3.751,05 | Alíquota: 15% | Dedução: 394.16
        (4664.68, 0.225, 675.49),  # De 3.751,06 até 4.664,68 | Alíquota: 22.5% | Dedução: 675.49
        (999999.00, 0.275, 908.73) # Acima de 4.664,68 | Alíquota: 27.5% | Dedução: 908.73
    ]
    
    if base_ir <= 0:
        return 0.0
        
    for teto, aliquota, deducao in faixas:
        if base_ir <= teto:
            return (base_ir * aliquota) - deducao
    
    # Caso caia na última faixa (acima do limite máximo)
    return (base_ir * faixas[-1][1]) - faixas[-1][2]


# --- 3. FUNÇÕES DE CÁLCULO (Lógica Trabalhista) ---

def calcular_meses_proporcionais(admissao, demissao):
    """Calcula os meses proporcionais para 13º e Férias (regra dos 15 dias)."""
    if demissao <= admissao:
        return 0
        
    # Usamos o dia 1 do mês de admissão para calcular a diferença
    admissao_mes_inicio = admissao.replace(day=1)
    
    # O cálculo deve considerar o mês de rescisão.
    # Se a demissão for antes do dia 15 do mês, o mês de demissão não conta.
    # Se for no dia 15 ou depois, o mês de demissão conta.
    
    if demissao.day < 15:
        # Se for antes do dia 15, contamos a diferença até o mês anterior.
        # Ex: Admissão: 01/01/2023, Demissão: 14/10/2023. Meses contados: Jan a Set (9 meses).
        demissao_mes_anterior = demissao.replace(day=1) - relativedelta(days=1)
        diferenca = relativedelta(demissao_mes_anterior, admissao_mes_inicio)
        total_meses = diferenca.years * 12 + diferenca.months + 1 # +1 para o mês de admissão
        
        # Correção para o caso em que a demissão ocorre no mesmo mês de admissão e antes do dia 15
        if total_meses < 0:
            return 0
        
        return total_meses
        
    else: # Dia 15 ou depois, o mês de demissão conta como completo
        # Ex: Admissão: 01/01/2023, Demissão: 15/10/2023. Meses contados: Jan a Out (10 meses).
        # Para fins de cálculo, consideramos a diferença do início do contrato até a data de demissão
        diferenca = relativedelta(demissao.replace(day=1), admissao.replace(day=1))
        total_meses = diferenca.years * 12 + diferenca.months + 1 # +1 para o mês de admissão
        return total_meses
        
def calcular_aviso_previo_indenizado(admissao, salario_base, dias_trabalhados_no_mes):
    """Calcula o Aviso Prévio Indenizado com a proporcionalidade da Lei 12.506/11."""
    
    # Diferença em anos completos
    diferenca = relativedelta(date.today(), admissao) # Calcula até hoje (simulação)
    anos_trabalhados = diferenca.years
    
    # Base: 30 dias (CLT)
    dias_aviso = 30 
    
    # Acréscimo: +3 dias por ano completo de trabalho (Lei 12.506/11), limitado a 60 dias adicionais (90 total)
    dias_adicionais = min(anos_trabalhados * 3, 60)
    dias_aviso += dias_adicionais
    
    valor_dia = salario_base / 30.0
    valor_ap = valor_dia * dias_aviso
    
    # O Aviso Prévio Indenizado não se confunde com o saldo de salário, mas é pago na rescisão
    return valor_ap, dias_aviso

def calcular_saldo_salario(salario_base, dias_trabalhados_no_mes):
    """Calcula o Saldo de Salário (dias trabalhados no último mês)."""
    valor_dia = salario_base / 30.0
    saldo = valor_dia * dias_trabalhados_no_mes
    return saldo

# --- 4. INTERFACE STREAMLIT ---

st.title("⚖️ Calculadora de Rescisão Trabalhista Completa")
st.markdown("### Simulação para Demissão **Sem Justa Causa** (Iniciativa do Empregador)")
st.caption("Esta ferramenta fornece uma estimativa de verbas rescisórias brutas e líquidas, incluindo Saldo de Salário, 13º, Férias, Aviso Prévio, Multa FGTS, e simulação de descontos (INSS/IRRF). **Não é um documento oficial.**")

st.markdown("---")

# 4.1. Entrada de Dados
col1, col2, col3 = st.columns(3)

with col1:
    salario_base = st.number_input(
        "1. Salário Mensal Bruto (R$):",
        min_value=0.01,
        value=3000.00,
        step=100.00,
        format="%.2f"
    )
    
with col2:
    saldo_fgts_base = st.number_input(
        "4. Saldo do FGTS (R$):",
        min_value=0.00,
        value=8000.00,
        step=100.00,
        format="%.2f",
        help="Saldo acumulado para cálculo da multa de 40%."
    )
    
with col3:
    dias_trabalhados = st.number_input(
        "5. Dias Trabalhados no Último Mês (0 a 30):",
        min_value=0,
        max_value=31,
        value=20,
        step=1,
        help="Dias trabalhados no mês da demissão (para Saldo de Salário)."
    )

col_adm, col_dem = st.columns(2)

with col_adm:
    data_admissao = st.date_input(
        "2. Data de Admissão (Início do Contrato):",
        value=date(2023, 1, 1),
    )

with col_dem:
    data_demissao = st.date_input(
        "3. Data de Demissão (Efetiva):",
        value=date.today(),
        min_value=data_admissao # Garante que a demissão seja após a admissão
    )

st.markdown("---")

# --- 5. CÁLCULO E EXIBIÇÃO ---

if st.button("Calcular Verbas Rescisórias Detalhadas", type="primary"):
    
    # 5.1. CÁLCULOS PRINCIPAIS
    
    # Meses para 13º e Férias Proporcionais
    meses_prop = calcular_meses_proporcionais(data_admissao, data_demissao)
    
    if meses_prop <= 0 and dias_trabalhados <= 0:
        st.error("Verifique as datas de Admissão e Demissão e/ou dias trabalhados. O cálculo não é possível.")
        st.stop()

    # Saldo de Salário
    valor_saldo_salario = calcular_saldo_salario(salario_base, dias_trabalhados)
    
    # 13º Salário Proporcional
    valor_13_proporcional = (salario_base / 12) * meses_prop
    
    # Férias Proporcionais (+ 1/3)
    valor_ferias_prop_base = (salario_base / 12) * meses_prop
    valor_terco_constitucional = valor_ferias_prop_base / 3
    valor_ferias_total = valor_ferias_prop_base + valor_terco_constitucional
    
    # Aviso Prévio Indenizado (AP)
    valor_ap, dias_ap = calcular_aviso_previo_indenizado(data_admissao, salario_base, dias_trabalhados)
    
    # Multa FGTS (40% para demissão sem justa causa)
    valor_multa_fgts = saldo_fgts_base * 0.40
    
    # TOTAL BRUTO
    total_verbas_brutas_tributaveis = valor_saldo_salario + valor_ap # As verbas de 13º e Férias têm tributação separada/isenta na prática.
    total_verbas_brutas = valor_saldo_salario + valor_ap + valor_13_proporcional + valor_ferias_total + valor_multa_fgts
    
    # 5.2. SIMULAÇÃO DE DESCONTOS (INSS e IRRF)
    
    # Base de cálculo do INSS é sobre as verbas tributáveis (SS + AP + 13º).
    # O INSS do 13º é descontado separadamente, mas para simplificação, vamos focar no INSS principal (SS + AP).
    
    # INSS: Base = Saldo de Salário + Aviso Prévio Indenizado
    inss_salario_ap = get_inss_aliquota_e_deducao(valor_saldo_salario + valor_ap)
    
    # IRRF: Base = Saldo de Salário + Aviso Prévio Indenizado - INSS principal
    base_irrf = (valor_saldo_salario + valor_ap) - inss_salario_ap
    irrf_principal = get_irrf_aliquota_e_deducao(base_irrf)
    
    # Desconto 13º (Na prática, o 13º tem INSS e IRRF específicos. Simplificando o INSS do 13º)
    inss_13 = get_inss_aliquota_e_deducao(valor_13_proporcional)
    # IRRF sobre o 13º é na fonte e exclusivo (tabela própria), que seria o correto, mas para simulação:
    irrf_13 = 0.0 # Simplificando a alíquota 0% para o 13º aqui.
    
    total_descontos = inss_salario_ap + irrf_principal + inss_13 + irrf_13
    
    # TOTAL LÍQUIDO SIMULADO (Atenção: FGTS é crédito, não entra no líquido de verbas, mas o saque é o valor total do FGTS + Multa)
    # Para o Total Líquido SIMULADO, consideramos as verbas pagas diretamente ao trabalhador:
    # Verbas Pagas (SS + AP + 13º + Férias) - Descontos
    # O FGTS e a Multa são sacados separadamente.
    
    verbas_pagas_liquidas = (valor_saldo_salario + valor_ap + valor_13_proporcional + valor_ferias_total) - total_descontos
    total_liquido_simulado = verbas_pagas_liquidas + saldo_fgts_base + valor_multa_fgts # Somando o saque FGTS + Multa para o 'total a receber'
    
    # 5.3. EXIBIÇÃO DOS RESULTADOS
    
    st.subheader(f"✅ Resumo dos Cálculos ({meses_prop} meses proporcionais)")
    
    col_liq, col_bruto, col_desc = st.columns(3)
    
    col_bruto.metric("💰 Total Verbas Brutas (Pagamento Direto)", f"R$ {valor_saldo_salario + valor_ap + valor_13_proporcional + valor_ferias_total:,.2f}")
    col_desc.metric("✂️ Total de Descontos (INSS/IRRF)", f"R$ {total_descontos:,.2f}", delta_color="inverse")
    col_liq.metric("💵 Total de Verbas Líquidas (Pagamento Direto)", f"R$ {verbas_pagas_liquidas:,.2f}")
    
    st.success(f"## ➕ Saque FGTS (Total a Receber): R$ {total_liquido_simulado:,.2f}")
    st.caption("O valor total a receber (Saque FGTS) inclui: Verbas Líquidas + Saldo FGTS + Multa FGTS. O depósito da multa é feito pelo empregador.")

    st.markdown("---")
    
    # 5.4. DETALHAMENTO E GRÁFICOS
    
    st.subheader("📊 Detalhamento de Valores")
    
    df_verbas = pd.DataFrame({
        'Verba': ['Saldo de Salário', '13º Salário Prop.', 'Férias Prop. (+1/3)', f'Aviso Prévio ({dias_ap} dias)', 'Multa FGTS (40%)'],
        'Valor Bruto (R$)': [valor_saldo_salario, valor_13_proporcional, valor_ferias_total, valor_ap, valor_multa_fgts],
        'Natureza': ['Tributável', 'Tributável', 'Isenta', 'Tributável', 'Isenta']
    })
    
    df_descontos = pd.DataFrame({
        'Desconto': ['INSS', 'IRRF'],
        'Valor (R$)': [inss_salario_ap + inss_13, irrf_principal + irrf_13],
        'Base': ['Salário, AP e 13º (Simulado)', 'Salário e AP (Após INSS)']
    })

    col_tabela, col_grafico = st.columns([1.5, 1])

    with col_tabela:
        st.markdown("#### Tabela de Verbas e Descontos")
        st.dataframe(df_verbas.style.format({'Valor Bruto (R$)': 'R$ {:,.2f}'}), use_container_width=True, hide_index=True)
        st.dataframe(df_descontos.style.format({'Valor (R$)': 'R$ {:,.2f}'}), use_container_width=True, hide_index=True)

    with col_grafico:
        st.markdown("#### Composição das Verbas Brutas (Pagamento Direto)")
        
        df_pie = pd.DataFrame({
            'Verba': ['Saldo de Salário', '13º Salário Prop.', 'Férias Prop. (+1/3)', f'Aviso Prévio ({dias_ap} dias)'],
            'Valor': [valor_saldo_salario, valor_13_proporcional, valor_ferias_total, valor_ap]
        })
        
        chart_pie = alt.Chart(df_pie).mark_arc(outerRadius=120).encode(
            theta=alt.Theta(field="Valor", type="quantitative"),
            color=alt.Color(field="Verba", type="nominal"),
            tooltip=['Verba', alt.Tooltip('Valor', format='$,.2f')]
        ).properties(
            title='Verbas Pagas Diretamente (Exclui FGTS/Multa)'
        )
        st.altair_chart(chart_pie, use_container_width=True)

    st.markdown("---")
    
    # 5.5. FONTES E FÓRMULAS
    
    st.subheader("💡 Fontes e Fórmulas Utilizadas")
    
    tab_fontes, tab_inss, tab_irrf = st.tabs(["Fórmulas Rescisórias", "Tabela INSS", "Tabela IRRF"])
    
    with tab_fontes:
        st.markdown("**1. Saldo de Salário (SS):**")
        st.latex(r"SS = \frac{Salário \: Base}{30} \times Dias \: Trabalhados \: no \: Mês")
        
        st.markdown("**2. Férias Proporcionais:**")
        st.latex(r"Férias \: Prop. = \frac{Salário \: Base}{12} \times Meses \: Prop.")
        st.latex(r"Terço \: Const. = \frac{Férias \: Prop.}{3}")
        st.latex(r"Férias \: Total = Férias \: Prop. + Terço \: Const.")
        st.caption("*Meses Proporcionais: A cada 12 meses de trabalho, o empregado tem direito a 30 dias de férias. Fracionamento considerado: 15 dias ou mais no mês contam como 1/12 avos.")
        
        st.markdown("**3. 13º Salário Proporcional:**")
        st.latex(r"13º \: Prop. = \frac{Salário \: Base}{12} \times Meses \: Prop.")
        st.caption("*Meses Proporcionais: A cada 12 meses, o empregado tem direito a 1/12 avos. Fracionamento considerado: 15 dias ou mais no mês contam como 1/12 avos.")
        
        st.markdown("**4. Aviso Prévio Indenizado (AP):**")
        st.latex(r"Dias \: AP = 30 \: dias \: + \: (3 \: dias \: \times \: Anos \: Completos \: de \: Serviço) \quad (\text{máx. } 90 \: dias)")
        st.latex(r"Valor \: AP = \frac{Salário \: Base}{30} \times Dias \: AP")
        st.caption("*Lei nº 12.506/11: Acréscimo de 3 dias por ano completo, limitado a 60 dias adicionais (totalizando 90 dias).")
        
        st.markdown("**5. Multa FGTS:**")
        st.latex(r"Multa \: FGTS = Saldo \: FGTS \: \times \: 40\%")
        st.caption("*Demissão Sem Justa Causa (Iniciativa do Empregador).")

    with tab_inss:
        st.markdown("#### Tabela Progressiva INSS (Exemplo 2025/2026)")
        st.markdown("O cálculo é progressivo (faixa a faixa) ou pela fórmula de dedução.")
        st.table(pd.DataFrame({
            'Salário (Até)': ['R$ 1.518,00', 'R$ 2.793,88', 'R$ 4.190,83', 'R$ 8.157,41 (Teto)'],
            'Alíquota': ['7,5%', '9,0%', '12,0%', '14,0%'],
            'Dedução (R$)': ['0,00', '22,77', '106,59', '190,40']
        }))
        st.latex(r"INSS = (Base \: C. \times Alíquota) - Parcela \: a \: Deduzir")
        st.caption("*Base de Cálculo INSS: Saldo de Salário + Aviso Prévio Indenizado + 13º Salário (cada um calculado separadamente na prática).")

    with tab_irrf:
        st.markdown("#### Tabela IRRF Mensal (Exemplo 2025/2026)")
        st.markdown("O cálculo é aplicado sobre a base de IR (Verbas Tributáveis - INSS).")
        st.table(pd.DataFrame({
            'Base C. (Até)': ['R$ 2.428,80', 'R$ 2.826,65', 'R$ 3.751,05', 'R$ 4.664,68', 'Acima'],
            'Alíquota': ['0%', '7,5%', '15,0%', '22,5%', '27,5%'],
            'Dedução (R$)': ['0,00', '182,16', '394,16', '675,49', '908,73']
        }))
        st.latex(r"IRRF = (Base \: C. \times Alíquota) - Parcela \: a \: Deduzir \: - \: Dedução \: por \: Dependente")
        st.caption("*Base de Cálculo IRRF: Saldo de Salário + Aviso Prévio - INSS. (Férias e Multa FGTS são isentas de IRRF).")

    st.markdown("---")
    st.warning("🚨 **Isenções:** Verbas como **Férias Indenizadas (+ 1/3)** e **Multa de 40% do FGTS** são legalmente isentas de Desconto de INSS e IRRF. Isso está considerado nos cálculos acima.")

# --- FIM DO CÓDIGO ---
