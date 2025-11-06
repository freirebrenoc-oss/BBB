import streamlit as st
from datetime import date
from dateutil.relativedelta import relativedelta
import pandas as pd
import altair as alt

# -----------------------
# Metadados / Fontes (links oficiais usados dentro do app)
# -----------------------
# Leis / Decretos / Portarias (fontes oficiais)
URL_CLT = "https://www.planalto.gov.br/ccivil_03/decreto-lei/del5452.htm"  # CLT (Decreto-Lei 5.452/1943)
URL_LEI_8036 = "https://www.planalto.gov.br/ccivil_03/leis/L8036consol.htm"  # Lei 8.036/1990 (FGTS)
URL_LEI_4090 = "https://www.planalto.gov.br/ccivil_03/leis/l4090.htm"  # Lei 4.090/1962 (13º)
URL_LEI_12506 = "https://www.planalto.gov.br/ccivil_03/_ato2011-2014/2011/lei/l12506.htm"  # Lei 12.506/2011 (aviso prévio proporcional)
URL_FGTS_CAIXA_PDF = "https://www.caixa.gov.br/Downloads/fgts-relatorios-avaliacao-programas/Lei_1990_08036.pdf"  # PDF Lei 8036/1990 (Caixa)
# INSS / Receita (tabelas / portarias por ano)
URL_INSS_2022_PORTARIA = "https://in.gov.br/en/web/dou/-/portaria-interministerial-mtp/me-n-12-de-17-de-janeiro-de-2022-375006998"  # Portaria 2022 (gov.br)
URL_INSS_2023_PORTARIA = "https://www.gov.br/previdencia/pt-br/assuntos/rpps/legislacao-dos-rpps/portarias/SEI_30818500_Portaria_Interministerial_26.pdf"  # Portaria 2023 (ex.: reajustes)
URL_INSS_2025_INFO = "https://www.gov.br/inss/pt-br/noticias/confira-como-ficaram-as-aliquotas-de-contribuicao-ao-inss"  # Página INSS (2025 - faixas)
URL_RECEITA_TABELAS = "https://www.gov.br/receitafederal/pt-br/assuntos/meu-imposto-de-renda/tabelas"  # Tabelas IR (Receita) - inclui 2024/2025
# -----------------------

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Calculadora Rescisória Simplificada (CLT) + Fontes Detalhadas",
    page_icon="⚖️",
    layout="wide"
)

# --- 2. TABELAS DE IMPOSTOS (Mantidas) ---

def get_inss_aliquota_e_deducao(salario_base):
    # Tabela INSS Progressiva (exemplo com valores de 2025; função compatível com 2022/2023/2025)
    # Faixas usadas no app (R$): 1.518,00 | 2.793,88 | 4.190,83 | 8.157,41
    faixas = [
        (1518.00, 0.075, 0.00),
        (2793.88, 0.09, 22.77),
        (4190.83, 0.12, 106.59),
        (8157.41, 0.14, 190.40)
    ]
    if salario_base <= 0:
        return 0.0
    base_calculo = min(salario_base, faixas[-1][0])
    
    for teto, aliquota, deducao in reversed(faixas):
        if base_calculo > teto:
            return (base_calculo * aliquota) - deducao
    return base_calculo * faixas[0][1]


def get_irrf_aliquota_e_deducao(base_ir):
    # Tabela IRRF usada no app (faixas e deduções que vigiaram em 2024/2025 até mudanças de maio/2025)
    faixas = [
        (2428.80, 0.00, 0.00),
        (2826.65, 0.075, 182.16),
        (3751.05, 0.15, 394.16),
        (4664.68, 0.225, 675.49),
        (999999.00, 0.275, 908.73)
    ]
    if base_ir <= 0:
        return 0.0
    for teto, aliquota, deducao in faixas:
        if base_ir <= teto:
            return (base_ir * aliquota) - deducao
    return (base_ir * faixas[-1][1]) - faixas[-1][2]

# --- 3. FUNÇÕES DE CÁLCULO (Lógica Trabalhista) ---

def calcular_meses_proporcionais(admissao, demissao):
    """
    Calcula os meses proporcionais para 13º e Férias:
    - Regra prática adotada: fracionamento de 15 dias ou mais conta como mês completo.
    - Implementação via relativedelta para obter meses completos entre as datas.
    """
    if demissao <= admissao:
        return 0, 0
    
    diferenca = relativedelta(demissao.replace(day=1), admissao.replace(day=1))
    total_meses = diferenca.years * 12 + diferenca.months + 1

    if demissao.day < 15 and diferenca.months > 0:
         total_meses -= 1
         
    return total_meses, total_meses 


def calcular_aviso_previo_indenizado(admissao, demissao, salario_base):
    """
    Aviso Prévio Indenizado:
    - Base legal: CLT art. 487 + Lei 12.506/2011 (acréscimo de 3 dias por ano completo, até 60 dias adicionais)
    - Dias = 30 dias + min(anos_completos*3, 60)
    """
    tempo_servico = relativedelta(demissao, admissao)
    anos_trabalhados = tempo_servico.years
    
    dias_ap = 30
    dias_adicionais = min(anos_trabalhados * 3, 60)
    dias_ap += dias_adicionais
    
    valor_dia = salario_base / 30.0
    valor_ap = valor_dia * dias_ap
    
    return valor_ap, dias_ap

def calcular_saldo_salario(salario_base, dias_trabalhados_no_mes):
    """Saldo de Salário = (salário / 30) * dias trabalhados (CLT - prática adotada)"""
    valor_dia = salario_base / 30.0
    saldo = valor_dia * dias_trabalhados_no_mes
    return saldo

# --- 4. INTERFACE STREAMLIT (Layout preservado) ---

st.title("⚖️ Calculadora de Rescisão Trabalhista Simplificada (CLT)")
st.markdown("### Mantive o layout original — removidas apenas férias vencidas e faltas injustificadas.")
st.caption("Simulação para Demissão Sem Justa Causa (Iniciativa do Empregador) — inclui INSS e IRRF (tabelas 2022 / 2023 / 2025 referenciadas).")

st.markdown("---")

# 4.1. Entrada de Dados
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
    # Saldo de Salário
    valor_saldo_salario = calcular_saldo_salario(salario_base, dias_trabalhados)
    
    # Meses proporcionais para 13º e férias proporcionais (fixo 30 dias/12 avos)
    meses_13_prop, meses_ferias_prop = calcular_meses_proporcionais(data_admissao, data_demissao)

    # 13º Salário Proporcional (Lei 4.090/62)
    valor_13_proporcional = (salario_base / 12) * meses_13_prop
    
    # Férias Proporcionais (sempre 30 dias / 12 avos) + 1/3 constitucional
    valor_ferias_prop_base = (salario_base / 12) * meses_ferias_prop
    valor_terco_prop = valor_ferias_prop_base / 3
    valor_ferias_prop_total = valor_ferias_prop_base + valor_terco_prop
    
    # Aviso Prévio Indenizado
    valor_ap, dias_ap = calcular_aviso_previo_indenizado(data_admissao, data_demissao, salario_base)
    
    # Multa FGTS (40%)
    valor_multa_fgts = saldo_fgts_base * 0.40
    
    # Descontos (INSS e IRRF)
    base_tributavel = valor_saldo_salario + valor_ap
    inss_principal = get_inss_aliquota_e_deducao(base_tributavel)
    inss_13 = get_inss_aliquota_e_deducao(valor_13_proporcional)

    base_irrf = base_tributavel - inss_principal
    irrf_principal = get_irrf_aliquota_e_deducao(base_irrf)
    
    total_descontos = inss_principal + irrf_principal + inss_13 
    
    # Totais
    verbas_brutas_diretas = valor_saldo_salario + valor_ap + valor_13_proporcional + valor_ferias_prop_total
    verbas_pagas_liquidas = verbas_brutas_diretas - total_descontos
    total_liquido_simulado = verbas_pagas_liquidas + saldo_fgts_base + valor_multa_fgts

    # --- EXIBIÇÃO ---
    st.subheader("✅ Resumo dos Cálculos")
    col_liq, col_bruto, col_desc = st.columns(3)
    col_bruto.metric("💰 Total Verbas Brutas (Pagamento Direto)", f"R$ {verbas_brutas_diretas:,.2f}")
    col_desc.metric("✂️ Total de Descontos (INSS/IRRF Simulado)", f"R$ {total_descontos:,.2f}", delta_color="inverse")
    col_liq.metric("💵 Total de Verbas Líquidas (Pagamento Direta)", f"R$ {verbas_pagas_liquidas:,.2f}")
    
    st.success(f"## ➕ Saque FGTS e Total a Receber: R$ {total_liquido_simulado:,.2f}")
    st.caption(f"Verbas Líquidas + Saldo FGTS ({saldo_fgts_base:,.2f}) + Multa FGTS ({valor_multa_fgts:,.2f}).")

    st.markdown("---")
    # 5.4. DETALHAMENTO E GRÁFICOS
    st.subheader("📊 Detalhamento de Valores")
    
    df_verbas = pd.DataFrame({
        'Verba': ['Saldo de Salário', '13º Salário Prop. (Avos)', 'Férias Proporcionais (+1/3)', 'Aviso Prévio', 'Multa FGTS (40%)'],
        'Valor Bruto (R$)': [valor_saldo_salario, valor_13_proporcional, valor_ferias_prop_total, valor_ap, valor_multa_fgts],
        'Natureza': ['Tributável (CLT, Art. 462)', 'Tributável (Lei 4.090/62)', 'Isenta (CLT, Art. 146)', 'Tributável (CLT, Art. 487)', 'Isenta (Lei 8.036/90)']
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
        st.markdown("#### Composição das Verbas Brutas (Pagamento Direto)")
        df_pie = pd.DataFrame({
            'Verba': ['Saldo Salário', '13º Prop.', 'Férias Prop.', 'Aviso Prévio'],
            'Valor': [valor_saldo_salario, valor_13_proporcional, valor_ferias_prop_total, valor_ap]
        })
        chart_pie = alt.Chart(df_pie).mark_arc(outerRadius=120).encode(
            theta=alt.Theta(field="Valor", type="quantitative"),
            color=alt.Color(field="Verba", type="nominal"),
            tooltip=['Verba', alt.Tooltip('Valor', format='$,.2f')]
        ).properties(title='Verbas Pagas Diretamente (Exclui FGTS/Multa)')
        st.altair_chart(chart_pie, use_container_width=True)

    st.markdown("---")

    # --- 5.5. FONTES E FÓRMULAS (ABAS) ---
    st.subheader("💡 Fontes, Fórmulas e Referências")
    tab_fontes, tab_inss, tab_irrf, tab_detalhadas = st.tabs([
        "Fórmulas e Referências CLT",
        "Tabela INSS (2022 / 2023 / 2025)",
        "Tabela IRRF (Resumo)",
        "📚 Fontes Detalhadas"
    ])

    with tab_fontes:
        st.markdown("**1. Saldo de Salário**")
        st.markdown(r"- Fórmula: `Saldo = (Salário / 30) * Dias Trabalhados`. (Prática adotada em folhas de pagamento).")
        st.caption("Base legal / referência: CLT (Decreto-Lei nº 5.452/1943).")
        st.markdown("**2. 13º Salário Proporcional**")
        st.markdown(r"- Fórmula: `13º Prop. = (Salário / 12) * Meses Trabalhados`.")
        st.caption(f"Base legal: Lei nº 4.090/1962. (Texto: {URL_LEI_4090})")
        st.markdown("**3. Férias Proporcionais + 1/3 Constitucional**")
        st.markdown(r"- Fórmula: `Férias Prop. = (Salário / 12) * Meses Prop.` + `1/3`.")
        st.caption("Base legal: CLT arts. 129/146; CF/88 art. 7º, XVII.")
        st.markdown("**4. Aviso Prévio Indenizado**")
        st.markdown(r"- Fórmula: `Dias AP = 30 + (3 dias × anos completos)` (máx. +60 dias). `Valor AP = (Salário / 30) × Dias AP`.")
        st.caption(f"Base legal: CLT art. 487; Lei 12.506/2011 (Texto: {URL_LEI_12506})")
        st.markdown("**5. Multa FGTS (40%)**")
        st.markdown(r"- Fórmula: `Multa FGTS = Saldo FGTS × 40%`.")
        st.caption(f"Base legal: Lei 8.036/1990 (Texto consolidado: {URL_LEI_8036})")

    with tab_inss:
        st.markdown("### Tabela INSS (resumo por ano)")
        st.markdown("- **2022**: alíquotas progressivas 7.5% / 9% / 12% / 14% (faixas ajustadas por portaria).")
        st.markdown(f"  - Portaria/ajustes (ex.): {URL_INSS_2022_PORTARIA}")
        st.markdown("- **2023**: atualização por Portaria Interministerial (reajustes e faixas).")
        st.markdown(f"  - Fonte exemplo: {URL_INSS_2023_PORTARIA}")
        st.markdown("- **2025**: faixas e deduções exemplificadas no app (7,5% / 9% / 12% / 14%).")
        st.markdown(f"  - Página INSS (informativo 2025): {URL_INSS_2025_INFO}")
        st.caption("Observação: provedores de folha atualizam faixas e deduções em portarias anuais — o app exibe a lógica prática (faixas + parcela a deduzir).")

    with tab_irrf:
        st.markdown("### Resumo IRRF (faixas e deduções aplicadas no app)")
        st.table(pd.DataFrame({
            'Base C. (Até)': ['R$ 2.428,80', 'R$ 2.826,65', 'R$ 3.751,05', 'R$ 4.664,68', 'Acima'],
            'Alíquota': ['0%', '7,5%', '15,0%', '22,5%', '27,5%'],
            'Dedução (R$)': ['0,00', '182,16', '394,16', '675,49', '908,73']
        }))
        st.caption(f"Fonte: Receita Federal — tabelas de incidência (página geral de tabelas): {URL_RECEITA_TABELAS}")

    with tab_detalhadas:
        st.markdown("## 📚 Fontes Detalhadas (textos oficiais e portarias)")
        st.markdown("**Legislação trabalhista e FGTS**")
        st.markdown(f"- CLT (Decreto-Lei nº 5.452/1943) — texto consolidado: {URL_CLT}")
        st.markdown(f"- Lei nº 8.036/1990 (FGTS) — texto consolidado/caixa: {URL_LEI_8036} / {URL_FGTS_CAIXA_PDF}")
        st.markdown(f"- Lei nº 4.090/1962 (13º salário): {URL_LEI_4090}")
        st.markdown(f"- Lei nº 12.506/2011 (aviso prévio proporcional): {URL_LEI_12506}")
        st.markdown("")
        st.markdown("**INSS — Portarias / comunicados por ano (exemplos oficiais)**")
        st.markdown(f"- Portaria Interministerial / Diário Oficial (2022): {URL_INSS_2022_PORTARIA}")
        st.markdown(f"- Portaria / comunicado (2023): {URL_INSS_2023_PORTARIA}")
        st.markdown(f"- Página/Informativo INSS (2025 — alíquotas/faixas): {URL_INSS_2025_INFO}")
        st.markdown("")
        st.markdown("**IR / Receita Federal (tabelas e instruções)**")
        st.markdown(f"- Páginas de tabelas da Receita Federal (IRPF 2024/2025): {URL_RECEITA_TABELAS}")
        st.markdown("")
        st.markdown("**Notas técnicas e observações**")
        st.markdown("- As faixas/parcelas deduzidas do INSS são publicadas em portarias anuais — o app usa a estrutura `faixas + parcela a deduzir` que é prática do mercado.")
        st.markdown("- A natureza tributária das verbas segue interpretações usuais: 13º, Saldo Salário e Aviso indenizado são tributáveis para INSS/IR (parte do mês); férias proporcionais geralmente têm natureza distinta para certos recolhimentos (o app trata como isenta para FGTS, tributável/isenções conforme prática).")
        st.caption("Se quiser, eu já deixo aqui no código comentários com citações de jurisprudência/TST relevantes — me fala se quer incluí-las.")

    st.markdown("---")
    st.info("⚠️ **Atenção:** Simulação baseada em dispositivos legais e em práticas de cálculo de folhas. Valores finais podem variar segundo Convenções Coletivas, acordos empresariais e decisões judiciais. Consulte sempre um profissional para casos concretos.")

# Fim do app
