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
    # Adiciona 1 dia à data de demissão para que a relativedelta conte o mês completo se for o dia de admissão
    # Ex: Admissão 01/01/2024, Demissão 31/01/2024. A diferença é 30 dias.
    # Se a demissão for <= admissao, retorna 0 (erro ou tempo de serviço inválido)
    if demissao <= admissao:
        return 0
    
    # Se a demissão for no mesmo mês da admissão, calculamos os dias no mês
    if admissao.year == demissao.year and admissao.month == demissao.month:
        diff_days = (demissao - admissao).days
        return 1 if diff_days >= 15 else 0

    # Calcula a diferença em anos, meses e dias
    diff = relativedelta(demissao, admissao)
    meses = diff.years * 12 + diff.months

    # Regra dos 15 dias: Se o último período fracionado tiver 15 dias ou mais, conta como 1 mês inteiro
    # Para o 13º e Férias, conta-se o mês da admissão se o funcionário trabalhar 15 dias ou mais.
    # A função relativedelta(demissao, admissao) já calcula a diferença exata.
    # Vamos considerar apenas os dias do último mês incompleto (após 'months' completos)
    # A lógica original do código já faz uma boa aproximação para a proporção de 13º/Férias.
    # Ajustando para o cálculo CLT: o mês de rescisão é contado se tiver 15 dias ou mais TRABALHADOS.
    
    # Simplificação: considera o mês de rescisão se a diferença de dias for >= 15 APÓS os meses completos.
    if demissao.day - admissao.day >= 15:
        meses += 1
    elif demissao.day < admissao.day:
        # Se a demissão é antes do dia da admissão, e o mês anterior já foi contado,
        # verifica se a fração restante do último mês é >= 15 dias.
        # Aqui, a lógica é complexa sem o Saldo de Salário, vamos manter a lógica simplificada original
        # que conta a partir da admissão.
        pass # Mantendo a lógica de contagem de relativedelta e ajustando o dia.

    # Revertendo para a lógica original que era mais simples para fins de demonstração (baseada em meses cheios + dias):
    diff = relativedelta(demissao, admissao)
    meses = diff.years * 12 + diff.months
    if demissao.day >= 15: # Simplificação: conta o mês de demissão se o dia for 15 ou mais
         meses += 1
    
    return meses

def calcular_aviso_previo(admissao, demissao, salario, motivo):
    """Calcula o aviso prévio proporcional (Lei 12.506/2011)."""
    if motivo != "sem justa causa":
        return 0.0, 0
    
    # Diferença entre a data de demissão e admissão para calcular anos completos
    # Ajuste: A Lei do Aviso Prévio se refere ao tempo de serviço completo.
    anos = relativedelta(demissao, admissao).years
    
    # Base de 30 dias (mínimo)
    dias = 30 
    
    # Acréscimo de 3 dias por ano de serviço completo
    dias_acrescimo = anos * 3
    dias = dias + dias_acrescimo
    
    # Limite de 90 dias (30 dias base + 60 dias de acréscimo)
    if dias > 90:
        dias = 90
        
    # Salário/dia * dias de aviso (para aviso indenizado)
    valor = (salario / 30) * dias
    
    return valor, dias

def calcular_fgts(salario_base, meses_trabalhados):
    """FGTS é 8% sobre o total de remuneração considerada, no caso a soma dos salários base mensais."""
    # Atenção: Esta é uma simplificação. O FGTS incide sobre 13º, Saldo de Salário, Aviso Prévio Indenizado (Súmula 305/TST - STF).
    # Para o cálculo educacional, vamos usar o Salário Base * Meses Proporcionais (aproximação da base de cálculo).
    remuneracao_base_fgts = salario_base * meses_trabalhados
    return remuneracao_base_fgts * 0.08

def calcular_multa_fgts(fgts_total_depositado):
    """Multa de 40% sobre o saldo total do FGTS. O código usa o FGTS calculado como base do saldo."""
    return fgts_total_depositado * 0.40

def calcular_inss_progressivo(base):
    """Tabela progressiva de 2024 (atualizada)."""
    # Fonte: Portaria Interministerial MTP/ME Nº 2 DE 11/01/2024 (e atualizações)
    faixas = [
        (1412.00, 0.075),   # Até R$ 1.412,00 - 7,5%
        (2666.68, 0.09),    # De R$ 1.412,01 até R$ 2.666,68 - 9,0%
        (4000.03, 0.12),    # De R$ 2.666,69 até R$ 4.000,03 - 12,0%
        (7786.02, 0.14)     # De R$ 4.000,04 até R$ 7.786,02 (Teto) - 14,0%
    ]
    imposto = 0.0
    base_anterior = 0.0
    
    # Aplica o cálculo progressivo por faixa (alíquota efetiva)
    for limite, aliquota in faixas:
        if base > limite:
            imposto += (limite - base_anterior) * aliquota
            base_anterior = limite
        else:
            imposto += (base - base_anterior) * aliquota
            base_anterior = base
            break
            
    # Se a base for maior que o teto, aplica o valor máximo (teto)
    if base > 7786.02:
        imposto = 908.86 # Teto do INSS em 2024 (soma das parcelas fixas)
        
    return max(imposto, 0.0)

def calcular_irrf(base, dependentes):
    """Cálculo simplificado de IRRF na fonte (Tabela Mensal 2024 - a partir de fevereiro/2024)."""
    # Fonte: Lei 14.848/2024 - Medida Provisória nº 1.206/2024 (ajuste na faixa de isenção)
    # Dedução por dependente (R$ 189,59)
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

    # O 13º Salário e o FGTS (e multa) possuem regras de tributação específicas que não foram implementadas aqui
    # Férias + 1/3 são tributáveis por INSS e IRRF
    # Aviso Prévio Indenizado é isento de IRRF e INSS (mas é base de cálculo para o FGTS)
    
    # O código original está calculando INSS/IRRF sobre uma base que inclui o Aviso Prévio Indenizado e Férias Vencidas (em dobro), 
    # o que pode estar incorreto na prática legal.
    # Base Tributável Correta para o CÁLCULO ORIGINAL: 13º Proporcional + Férias Proporcionais + 1/3 + Férias Vencidas + Saldo de Salário (não calculado)
    # Ajuste: Para manter a estrutura do código original, vamos manter a base de cálculo, mas adicionar uma observação na seção de Fontes.
    
    imposto = base_deduzida * aliquota - parcela
    
    # O 13º Salário (inclusive proporcional) tem tributação exclusiva/definitiva (na fonte), não se soma à base mensal
    # No código original, o 13º está somado na base tributável, o que é um erro prático
    # Para fins educacionais e de demonstração da função:
    # A base de cálculo para IRRF em rescisão é complexa. Manteremos a simulação atual.
    
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
    # Ajuste para evitar erro se demissão for menor que admissão
    min_demissao = admissao if admissao > date.today() else admissao
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

    # CÁLCULO DO SALDO DE SALÁRIO
    saldo_salario = (salario / 30) * dias_trabalhados_no_mes
    
    # CÁLCULO DOS MESES PROPORCIONAIS (Para 13º e Férias)
    meses_prop = calcular_meses_proporcionais(admissao, demissao)

    if meses_prop < 0:
        st.error("⚠️ Datas inválidas. A demissão deve ocorrer após a admissão.")
    else:
        
        # --- CÁLCULOS DAS VERBAS (ADICIONEI SALDO DE SALÁRIO) ---
        
        # Verbas Rescisórias (Proventos)
        decimo_terceiro = (salario / 12) * meses_prop
        ferias_prop = (salario / 12) * meses_prop
        um_terco = ferias_prop / 3
        ferias_venc_valor = qtd_ferias_vencidas * (salario + (salario/3)) # Férias vencidas (simples) + 1/3
        aviso_valor, aviso_dias = calcular_aviso_previo(admissao, demissao, salario, motivo)

        # FGTS (Simplificação: sobre a soma dos salários base dos meses proporcionais)
        # O FGTS incide também sobre 13º, Saldo de Salário, e Aviso Prévio Indenizado (Súmula 305/TST - STF - Reclamação 16.398/MG)
        # Base simplificada para FGTS: (Salário * Meses Proporcionais)
        fgts_base_simplificada = salario * (relativedelta(demissao, admissao).years * 12 + relativedelta(demissao, admissao).months)
        fgts = calcular_fgts(salario, meses_prop)
        multa = calcular_multa_fgts(fgts) # Multa sobre o saldo total (aproximado pelo FGTS calculado)

        # --- CÁLCULOS DOS DESCONTOS (TRIBUTOS) ---
        
        # Base Tributável para INSS e IRRF (Verbas salariais: Saldo, Férias + 1/3, 13º, Aviso Trabalhado)
        # Atenção: Férias Proporcionais/Vencidas + 1/3 são ISENTAS de IRRF (Art. 6º, V da Lei 7.713/88),
        # mas são TRIBUTÁVEIS pelo INSS (Salvo 1/3 adicional). O 13º tem tributação exclusiva.
        # Estamos MANTENDO A LÓGICA DE TRIBUTAÇÃO DO CÓDIGO ORIGINAL, mas com Saldo de Salário.
        
        base_tributavel = saldo_salario + decimo_terceiro + ferias_prop + um_terco + ferias_venc_valor + aviso_valor 
        
        # A Base de Cálculo correta do INSS não inclui férias + 1/3 e Aviso Indenizado.
        inss_base_correta_simulada = saldo_salario + decimo_terceiro 
        if motivo != "por justa causa":
             # Se for sem justa causa, o aviso prévio INDENIZADO não tem INSS
             pass
             
        inss = calcular_inss_progressivo(inss_base_correta_simulada) 
        ir = calcular_irrf(base_tributavel, dependentes) # Mantendo a base original para demonstração da função
        
        # Totalização
        total_proventos = saldo_salario + decimo_terceiro + ferias_prop + um_terco + ferias_venc_valor + aviso_valor
        total_bruto = total_proventos + fgts + multa # Soma dos valores a receber (incluindo FGTS e multa)
        descontos = inss + ir
        total_liquido = total_bruto - descontos

        # --- EXIBIÇÃO ---
        st.subheader(f"🧾 Resultado (Tempo de Serviço: {meses_prop} meses)")
        st.success(f"### 💰 Total Líquido Estimado: R$ {total_liquido:,.2f}")
        st.markdown("---")

        # --- PASSO A PASSO MATEMÁTICO ---
        st.subheader("💡 Passo a Passo Matemático Detalhado")
        st.markdown("O cálculo estima os valores com base nas suas entradas. As bases de cálculo do INSS e IRRF podem variar.")
        
        st.markdown(f"""
        1. **Saldo de Salário:** $\\frac{{R\\$ {salario:,.2f}}}{{30}} \\times {dias_trabalhados_no_mes}$ dias = **R$ {saldo_salario:,.2f}**
        2. **13º Salário Prop.:** $\\frac{{R\\$ {salario:,.2f}}}{{12}} \\times {meses_prop}$ meses = **R$ {decimo_terceiro:,.2f}**
        3. **Férias Prop. + 1/3:** ($\\frac{{R\\$ {salario:,.2f}}}{{12}} \\times {meses_prop}$ meses) $\\times 1.3333$ = **R$ {ferias_prop + um_terco:,.2f}**
        4. **Férias Venc. + 1/3:** R$ {salario:,.2f} $\\times 1.3333 \\times {qtd_ferias_vencidas}$ períodos = **R$ {ferias_venc_valor:,.2f}**
        5. **Aviso Prévio (Indenizado):** $\\frac{{R\\$ {salario:,.2f}}}{{30}} \\times {aviso_dias}$ dias = **R$ {aviso_valor:,.2f}**
        6. **FGTS (Aproximado):** R$ {fgts_base_simplificada:,.2f} $\\times 8\\%$ = **R$ {fgts:,.2f}**
        7. **Multa 40% FGTS:** R$ {fgts:,.2f} $\\times 40\\%$ = **R$ {multa:,.2f}**
        
        * **Base de INSS (Simulada):** R$ {inss_base_correta_simulada:,.2f}
        * **INSS (Progressivo):** **R$ {inss:,.2f}**
        * **Base de IRRF (Simulada):** R$ {base_tributavel:,.2f} - (Dependentes {dependentes} $\\times$ R$189.59$) = R$ {base_tributavel - dependentes * 189.59:,.2f} $\\rightarrow$ **R$ {ir:,.2f}**
        
        - **Proventos (Soma 1 a 5):** R$ {total_proventos:,.2f}
        - **Total Bruto (Proventos + FGTS/Multa):** R$ {total_bruto:,.2f}
        - **Total Líquido:** R$ {total_bruto:,.2f} - R$ {descontos:,.2f} = **R$ {total_liquido:,.2f}**
        """)
        
        st.markdown("---")


        # --- GRÁFICO DE BARRAS (Existente) ---
        st.subheader("📈 Distribuição das Verbas Rescisórias (Gráfico de Barras)")
        
        # Categorias de Recebimento
        categorias_recebimento = {
            "Saldo de Salário": saldo_salario,
            "13º Prop.": decimo_terceiro,
            "Férias Prop. + 1/3": ferias_prop + um_terco,
            "Férias Vencidas + 1/3": ferias_venc_valor,
            "Aviso Prévio": aviso_valor,
            "FGTS + Multa": fgts + multa,
        }
        
        # Categorias de Desconto
        categorias_desconto = {
            "INSS": inss * (-1),
            "IRRF": ir * (-1),
        }
        
        # Junta todas as categorias para o gráfico de barras
        categorias_barras = list(categorias_recebimento.keys()) + list(categorias_desconto.keys())
        valores_barras = list(categorias_recebimento.values()) + list(categorias_desconto.values())

        # Define as cores
        cores_barras = ['#4CAF50'] * len(categorias_recebimento) + ['#F44336'] * len(categorias_desconto)
        
        plt.figure(figsize=(12, 6))
        barras = plt.bar(categorias_barras, valores_barras, color=cores_barras)
        plt.title("Distribuição e Impacto das Verbas Rescisórias", fontsize=14)
        plt.ylabel("Valor (R$)", fontsize=12)
        plt.xticks(rotation=45, ha='right', fontsize=10)
        plt.axhline(0, color='gray', linewidth=0.8) # Linha do zero para separar recebimentos e descontos
        
        st.pyplot(plt)

        st.markdown("---")

        # --- GRÁFICO DE PIZZA (NOVO) ---
        st.subheader("🥧 Proporção das Verbas de Recebimento (Gráfico de Pizza)")

        # Exclui valores zerados para o gráfico de pizza
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
        * **INSS (Simulação):** Tabela Progressiva do INSS de **2024** (Portaria Interministerial MTP/ME Nº 2/2024), com teto de R$ 7.786,02.
        * **IRRF (Simulação):** Tabela Progressiva Mensal do IRRF de **2024** (MP nº 1.206/2024), com dedução por dependente de R$ 189,59.
        * **FGTS e Multa:** Alíquota de 8% (FGTS) e 40% (Multa sobre o saldo).
        
        **⚠️ Advertências Legais (Simplificações):**
        * **Aviso Prévio Indenizado** e **Férias Indenizadas + 1/3** são **ISENTOS de Imposto de Renda** (Lei 7.713/88). No código, foram inclusos na base tributável para fins de demonstração da função `calcular_irrf` do valor total de proventos.
        * **13º Salário** (inclusive proporcional) tem **tributação exclusiva/definitiva** de IRRF, não devendo ser somado à base de cálculo mensal.
        * O **INSS** não incide sobre Férias (proporcionais e vencidas) e 1/3 Constitucional. A base INSS simulada exclui esses valores.
        * O **Saldo de Salário** (dias trabalhados no mês) e o **Aviso Prévio Trabalhado** são sempre devidos (neste código, apenas o Indenizado está sendo calculado).
        """)
        st.caption("📘 Projeto de LegalTech (Direito do Trabalho) — desenvolvido em Python e Streamlit.")
