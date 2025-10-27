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

# Função para calcular meses proporcionais
def calcular_meses_proporcionais(admissao, demissao):
    """Calcula os meses proporcionais (com a regra dos 15 dias)."""
    if demissao <= admissao:
        return 0
    diferenca = relativedelta(demissao, admissao)
    total_meses = diferenca.years * 12 + diferenca.months
    if diferenca.days >= 15:
        total_meses += 1
    return total_meses

# Função para calcular o Aviso Prévio
def calcular_aviso_previo(admissao, demissao, salario_base, motivo_rescisao):
    """
    Calcula o aviso prévio proporcional ao tempo de serviço.
    Retorna (valor_em_reais, dias_de_aviso).
    Limite de 90 dias (30 + 3*dias até 90).
    """
    diferenca = relativedelta(demissao, admissao)
    anos_trabalhados = diferenca.years
    dias_aviso_previo = 30 + anos_trabalhados * 3  # 30 dias + 3 dias por ano de serviço
    # Limita a 90 dias conforme Lei 12.506/2011
    if dias_aviso_previo > 90:
        dias_aviso_previo = 90

    if motivo_rescisao == "sem justa causa":
        valor_aviso_previo = (salario_base / 30) * dias_aviso_previo  # Aviso prévio proporcional
    else:
        valor_aviso_previo = 0  # Aviso prévio não é pago em caso de demissão por justa causa
    return valor_aviso_previo, dias_aviso_previo

# Função para calcular o FGTS
def calcular_fgts(salario_base, meses_trabalhados):
    """Calcula o valor do FGTS a ser pago (8% por mês)."""
    return salario_base * 0.08 * meses_trabalhados

# Função para calcular a Multa do FGTS
def calcular_multa_fgts(fgts):
    """Calcula a multa de 40% sobre o saldo do FGTS."""
    return fgts * 0.40

# Função INSS progressivo (corrigida)
def calcular_inss_progressivo(base):
    """
    Calcula o INSS de forma progressiva sobre a base informada.
    Retorna o valor do INSS.
    Faixas utilizadas (ex.: faixas aproximadas vigentes históricamente).
    """
    faixas = [
        (1412.00, 0.075),
        (2666.68, 0.09),
        (4000.03, 0.12),
        (7786.02, 0.14)  # teto usado como limite superior das faixas
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
    # se passou por todas as faixas (base maior que último limite), aplica última alíquota até o teto
    return max(imposto, 0.0)

# Função IR para rescisão (base = 13º + férias + aviso) com dependentes
def calcular_ir_rescisao(base_ir, dependentes):
    """
    Calcula o IRRF sobre a base de rescisão (13º + férias + aviso).
    Considera dedução por dependente (R$ 189.59 por dependente).
    Retorna (valor_ir, aliquota_pct, parcela_deduzir).
    Observação: usamos a tabela progressiva padrão (parcelas a deduzir).
    """
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
        value=date(2013, 1, 1),
    )
with col_dem:
    data_demissao = st.date_input(
        "3. Data de Demissão (Fim do Contrato):",
        value=date.today(),
        min_value=data_admissao
    )

# Pergunta sobre o motivo da rescisão
motivo_rescisao = st.selectbox(
    "4. Qual o motivo da rescisão?",
    ["sem justa causa", "por justa causa"]
)

# Pergunta sobre o número de dependentes
dependentes = st.number_input(
    "5. Número de dependentes para o Imposto de Renda:",
    min_value=0,
    max_value=10,
    value=0
)

# Pergunta sobre férias vencidas no ano anterior
ferias_vencidas = st.radio(
    "6. Houve férias vencidas no ano anterior?",
    ("Não", "Sim")
)

if ferias_vencidas == "Sim":
    num_ferias_vencidas = st.number_input(
        "Quantas férias vencidas houveram no ano anterior? (nº de períodos de 30 dias):",
        min_value=0,
        max_value=5,
        value=0
    )
else:
    num_ferias_vencidas = 0

st.markdown("---")

# --- 4. CÁLCULO E EXIBIÇÃO ---
if st.button("Calcular Verbas Rescisórias", type="primary"):
    meses_trabalhados = calcular_meses_proporcionais(data_admissao, data_demissao)

    if meses_trabalhados <= 0:
        st.error("Verifique as datas de Admissão e Demissão. O cálculo não é possível.")
    else:
        # Cálculos das verbas rescisórias
        valor_13_proporcional = (salario_base / 12) * meses_trabalhados
        valor_ferias_prop_base = (salario_base / 12) * meses_trabalhados
        valor_terco_constitucional = valor_ferias_prop_base / 3
        # acrescenta férias vencidas (cada uma é ~1 salário)
        valor_ferias_total = valor_ferias_prop_base + valor_terco_constitucional + (num_ferias_vencidas * salario_base)
        valor_aviso_previo, dias_aviso = calcular_aviso_previo(data_admissao, data_demissao, salario_base, motivo_rescisao)
        fgts = calcular_fgts(salario_base, meses_trabalhados)
        multa_fgts = calcular_multa_fgts(fgts)

        # BASES CORRETAS: FGTS e multa NÃO entram na base de INSS/IR
        base_tributavel = valor_13_proporcional + valor_ferias_total + valor_aviso_previo

        # Cálculo INSS (progressivo) sobre a base tributável
        inss = calcular_inss_progressivo(base_tributavel)

        # Cálculo IR sobre base tributável com dependentes
        ir, ir_aliquota_pct, ir_parcela, deducao_dependentes = calcular_ir_rescisao(base_tributavel, dependentes)

        # Totais
        total_bruto_rescisao = valor_13_proporcional + valor_ferias_total + valor_aviso_previo + fgts + multa_fgts
        total_descontos = inss + ir
        total_devido = total_bruto_rescisao - total_descontos

        # --- EXIBIÇÃO DOS RESULTADOS (Métricas Essenciais) ---
        st.subheader(f"Resultado Completo (Meses Contados: {meses_trabalhados})")
        st.success(f"### TOTAL ESTIMADO DEVIDO: R$ {total_devido:,.2f}")
        st.markdown("---")

        # Passo a passo do cálculo:
        st.markdown("### Passo a Passo do Cálculo:")

        st.write(f"1. **13º Salário Proporcional**: \n\n"
                 f"Fórmula: `(Salário Mensal / 12) * Meses Trabalhados`\n"
                 f"Valor: R$ {valor_13_proporcional:,.2f}")

        st.write(f"2. **Férias Proporcionais (+ 1/3)**: \n\n"
                 f"Fórmula para férias: `(Salário Mensal / 12) * Meses Trabalhados`\n"
                 f"Fórmula para 1/3 adicional: `Férias Proporcionais / 3`\n"
                 f"Valor Total: R$ {valor_ferias_total:,.2f} (1/3 Adicional: R$ {valor_terco_constitucional:,.2f})")

        st.write(f"3. **Aviso Prévio**: \n\n"
                 f"Fórmula: `(Salário Mensal / 30) * (dias)` onde dias = 30 + 3 * Anos de Serviço (limitado a 90 dias)\n"
                 f"Dias calculados: {dias_aviso} dias\n"
                 f"Valor: R$ {valor_aviso_previo:,.2f}")

        st.write(f"4. **FGTS**: \n\n"
                 f"Fórmula: `Salário Mensal * 0.08 * Meses Trabalhados`\n"
                 f"Valor: R$ {fgts:,.2f}")

        st.write(f"5. **Multa do FGTS (40%)**: \n\n"
                 f"Fórmula: `FGTS * 0.40`\n"
                 f"Valor: R$ {multa_fgts:,.2f}")

        st.write(f"6. **INSS (progressivo)**: \n\n"
                 f"Base usada (13º + férias + aviso): R$ {base_tributavel:,.2f}\n"
                 f"Valor calculado do INSS: R$ {inss:,.2f}")

        st.write(f"7. **Imposto de Renda (IR)**: \n\n"
                 f"Base após deduções por dependente: R$ {base_tributavel - deducao_dependentes:,.2f}\n"
                 f"Deduções por dependente (R$ 189,59/unid): R$ {deducao_dependentes:,.2f}\n"
                 f"Alíquota aplicada: {ir_aliquota_pct:.1f}%; Parcela a deduzir: R$ {ir_parcela:,.2f}\n"
                 f"Valor do IR: R$ {ir:,.2f}")

        st.write(f"**Total Bruto (sem deduções)**: R$ {total_bruto_rescisao:,.2f}")
        st.write(f"**Total Descontos (INSS + IR)**: R$ {total_descontos:,.2f}")
        st.write(f"**Total Devido (com deduções)**: R$ {total_devido:,.2f}")

        # --- Gráfico de Barras com todas as verbas ---
        def plot_grafico_verbas_rescisorias(valor_13, valor_ferias, valor_terco, aviso, fgts_v, multa, inss_v, ir_v):
            categorias = ['13º Salário', 'Férias Proporcionais', '1/3 Adicional', 'Aviso Prévio', 'FGTS', 'Multa FGTS', 'INSS', 'IR']
            valores = [valor_13, valor_ferias, valor_terco, aviso, fgts_v, multa, inss_v, ir_v]

            plt.figure(figsize=(10, 6))
            plt.bar(categorias, valores)
            plt.title('Distribuição das Verbas Rescisórias', fontsize=14)
            plt.xlabel('Categorias de Verbas', fontsize=12)
            plt.ylabel('Valor (R$)', fontsize=12)
            plt.xticks(rotation=45)
            st.pyplot(plt)

        plot_grafico_verbas_rescisorias(valor_13_proporcional, valor_ferias_prop_base, valor_terco_constitucional, valor_aviso_previo, fgts, multa_fgts, inss, ir)

        # --- Gráfico de Pizza (Percentual de cada parte do total) ---
        def plot_grafico_pizza(valor_13, valor_ferias, valor_terco, aviso, fgts_v, multa, inss_v, ir_v, total):
            categorias = ['13º Salário', 'Férias Proporcionais', '1/3 Adicional', 'Aviso Prévio', 'FGTS', 'Multa FGTS', 'INSS', 'IR']
            valores = [valor_13, valor_ferias, valor_terco, aviso, fgts_v, multa, inss_v, ir_v]
            # evita divisão por zero
            total_calc = total if total != 0 else 1
            porcentagens = [v / total_calc * 100 for v in valores]

            plt.figure(figsize=(8, 8))
            plt.pie(porcentagens, labels=categorias, autopct='%1.1f%%', startangle=90)
            plt.title('Distribuição Percentual das Verbas Rescisórias', fontsize=14)
            st.pyplot(plt)

        plot_grafico_pizza(valor_13_proporcional, valor_ferias_total, valor_terco_constitucional, valor_aviso_previo, fgts, multa_fgts, inss, ir, total_bruto_rescisao)

        st.markdown("---")
        st.info("⚠️ **Atenção:** Este é um cálculo aproximado e padronizado para casos típicos de rescisão sem justa causa. Situações específicas (aviso trabalhado, férias vencidas/indenizadas distintas, descontos judiciais, verbas indenizatórias ou acordos) podem alterar os resultados. Consulte um contador ou advogado trabalhista para casos reais.")

        # --- Fontes ---
        st.markdown("### Fontes / Referências")
        st.markdown("- Lei nº 4.090/1962 (13º salário).")
        st.markdown("- CLT (férias, aviso prévio - art. 487).")
        st.markdown("- Lei nº 8.036/1990 (FGTS).")
        st.markdown("- Lei nº 12.506/2011 (aviso prévio proporcional).")
        st.markdown("- Tabelas de IR e INSS aplicadas conforme uso comum em apps de cálculo (ajustar conforme normativos da Receita/INSS quando necessário).")
        st.caption("Projeto de LegalTech (Direito do Trabalho) com Python e Streamlit. Referência de consulta prática: https://www.calculadorafacil.com.br/trabalhista/calcular-rescisao")
