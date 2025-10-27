# arquivo: calculadora_rescisao.py
import streamlit as st
from datetime import date
from dateutil.relativedelta import relativedelta
import matplotlib.pyplot as plt
import pandas as pd
import io

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Calculadora Rescisória Completa",
    page_icon="👷",
    layout="centered"
)

# --- 2. FUNÇÕES DE CÁLCULO (tudo relacionado à rescisão) ---

def calcular_meses_proporcionais(admissao, demissao):
    """Calcula meses proporcionais, com regra dos 15 dias (rescisão)."""
    if demissao <= admissao:
        return 0
    diferenca = relativedelta(demissao, admissao)
    meses = diferenca.years * 12 + diferenca.months
    if diferenca.days >= 15:
        meses += 1
    return meses

def calcular_aviso_previo(admissao, demissao, salario):
    """Aviso prévio indenizado: 30 dias + 3 dias por ano completo (rescisão)."""
    anos = relativedelta(demissao, admissao).years
    dias = 30 + (anos * 3)
    return (salario / 30) * dias

def calcular_fgts(salario, meses):
    """FGTS relativo aos meses trabalhados (8%). Em rescisão, mostramos o saldo acumulado."""
    return salario * 0.08 * meses

def calcular_multa_fgts(fgts):
    """Multa rescisória de 40% sobre o FGTS (rescisão sem justa causa)."""
    return fgts * 0.40

def calcular_inss_progressivo(valor_base):
    """
    Calcula INSS de forma progressiva (tabela por faixas).
    Usamos como base as verbas salariais tributáveis na rescisão.
    """
    faixas = [
        (1412.00, 0.075),
        (2666.68, 0.09),
        (4000.03, 0.12),
        (7786.02, 0.14)
    ]
    imposto = 0.0
    base_anterior = 0.0

    for limite, aliquota in faixas:
        if valor_base > limite:
            imposto += (limite - base_anterior) * aliquota
            base_anterior = limite
        else:
            imposto += (valor_base - base_anterior) * aliquota
            break
    return max(imposto, 0.0)

def calcular_ir_rescisao(base_ir):
    """
    Calcula IRRF sobre as verbas tributáveis da rescisão (13º, férias +1/3 e aviso indenizado).
    Retorna (valor_ir, aliquota_usada_em_percent).
    As deduções/parcelas seguem a tabela progressiva (ex.: Parcela a deduzir).
    """
    if base_ir <= 2112.00:
        aliquota, deducao = 0.0, 0.0
    elif base_ir <= 2826.65:
        aliquota, deducao = 0.075, 158.40
    elif base_ir <= 3751.05:
        aliquota, deducao = 0.15, 370.40
    elif base_ir <= 4664.68:
        aliquota, deducao = 0.225, 651.73
    else:
        aliquota, deducao = 0.275, 884.96

    imposto = (base_ir * aliquota) - deducao
    return max(imposto, 0.0), aliquota * 100

# --- 3. INTERFACE (tudo sobre rescisão) ---
st.title("👷 Calculadora Completa de Rescisão Trabalhista")
st.markdown("Cálculo de verbas rescisórias: **13º proporcional, férias +1/3, aviso prévio, FGTS, multa do FGTS, INSS e IRRF**.")
st.caption("Observação: simplificação para casos típicos de rescisão sem justa causa. Ajustes podem ser necessários para situações específicas.")

st.markdown("---")

# Entradas
salario_base = st.number_input("💰 Salário Mensal Bruto (R$):", min_value=0.01, value=2000.00, step=50.00, format="%.2f")
col_adm, col_dem = st.columns(2)
with col_adm:
    data_admissao = st.date_input("📅 Data de Admissão:", value=date(2023, 1, 1))
with col_dem:
    data_demissao = st.date_input("📆 Data de Demissão:", value=date.today(), min_value=data_admissao)

# Botão de cálculo
st.markdown("---")
if st.button("Calcular Rescisão", type="primary"):
    meses_trabalhados = calcular_meses_proporcionais(data_admissao, data_demissao)

    if meses_trabalhados <= 0:
        st.error("❌ Verifique as datas: a demissão deve ser posterior à admissão.")
    else:
        # --- Verbas rescisórias (tudo sobre rescisão) ---
        decimo_prop = (salario_base / 12) * meses_trabalhados
        ferias_prop = (salario_base / 12) * meses_trabalhados
        terco = ferias_prop / 3
        ferias_total = ferias_prop + terco
        aviso = calcular_aviso_previo(data_admissao, data_demissao, salario_base)

        # FGTS e multa (não entram na base de IR)
        fgts_saldo = calcular_fgts(salario_base, meses_trabalhados)
        multa_fgts = calcular_multa_fgts(fgts_saldo)

        # Base do IR e INSS = somente verbas tributáveis (13º, férias+1/3, aviso)
        base_tributavel = decimo_prop + ferias_total + aviso

        # Cálculo IR e INSS (aplicados sobre a base correta)
        ir_valor, ir_aliquota_pct = calcular_ir_rescisao(base_tributavel)
        inss_valor = calcular_inss_progressivo(base_tributavel)

        # Totais
        total_bruto_rescisao = decimo_prop + ferias_total + aviso + fgts_saldo + multa_fgts
        total_descontos = ir_valor + inss_valor
        total_liquido = total_bruto_rescisao - total_descontos

        # --- Exibição ---
        st.subheader(f"🧾 Resultado (Meses considerados: {meses_trabalhados})")
        st.success(f"**Total Líquido Estimado (rescisão): R$ {total_liquido:,.2f}**")
        st.markdown("---")

        st.markdown("### Detalhamento (tudo referente à rescisão)")
        st.write(f"• 13º Salário Proporcional: R$ {decimo_prop:,.2f}")
        st.write(f"• Férias Proporcionais: R$ {ferias_prop:,.2f}")
        st.write(f"• 1/3 Constitucional sobre Férias: R$ {terco:,.2f}")
        st.write(f"• Total de Férias (+1/3): R$ {ferias_total:,.2f}")
        st.write(f"• Aviso Prévio Indenizado: R$ {aviso:,.2f}")
        st.write(f"• FGTS (8% sobre remunerações consideradas): R$ {fgts_saldo:,.2f}")
        st.write(f"• Multa de 40% sobre FGTS: R$ {multa_fgts:,.2f}")
        st.markdown("---")
        st.write(f"• Base Tributável (13º + Férias + Aviso): R$ {base_tributavel:,.2f}")
        st.write(f"• INSS (progressivo sobre base tributável): R$ {inss_valor:,.2f}")
        st.write(f"• IRRF (alíquota aplicada: {ir_aliquota_pct:.1f}%): R$ {ir_valor:,.2f}")
        st.markdown("---")
        st.write(f"**Total Bruto (todas as verbas): R$ {total_bruto_rescisao:,.2f}**")
        st.write(f"**Total Descontos (INSS + IR): R$ {total_descontos:,.2f}**")
        st.write(f"**Total Líquido Estimado (após descontos): R$ {total_liquido:,.2f}**")

        # --- Gráfico de barras (verbas rescisórias) ---
        categorias = ['13º Prop.', 'Férias Prop.', '1/3 Férias', 'Aviso', 'FGTS', 'Multa FGTS', 'INSS', 'IR']
        valores = [decimo_prop, ferias_prop, terco, aviso, fgts_saldo, multa_fgts, inss_valor, ir_valor]

        plt.figure(figsize=(9,5))
        plt.bar(categorias, valores)
        plt.title('Distribuição das Verbas na Rescisão')
        plt.xlabel('Verbas')
        plt.ylabel('Valor (R$)')
        plt.xticks(rotation=30)
        st.pyplot(plt, use_container_width=True)

        # --- Gráfico pizza (percentual sobre o total bruto) ---
        # Evita divisão por zero
        total_for_pct = sum([abs(v) for v in valores]) or 1
        porcentagens = [v / total_for_pct * 100 for v in valores]

        plt.figure(figsize=(6,6))
        plt.pie(porcentagens, labels=categorias, autopct='%1.1f%%', startangle=90)
        plt.title('Percentual de Cada Verba (rescisão)')
        st.pyplot(plt, use_container_width=True)

        st.markdown("---")
        st.info("⚠️ Atenção: este cálculo é uma simplificação para casos típicos de rescisão sem justa causa. Ajustes podem ser necessários (ex.: aviso trabalhado, férias vencidas/indenizadas, dependentes, deduções legais específicas, parcelamentos etc.).")

        # --- Exportar resultados (CSV) ---
        df = pd.DataFrame({
            "Item": categorias + ["Total Bruto", "Total Descontos", "Total Líquido"],
            "Valor (R$)": valores + [total_bruto_rescisao, total_descontos, total_liquido]
        })

        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("⬇️ Baixar resumo da rescisão (CSV)", data=csv, file_name="rescisao_resumo.csv", mime="text/csv")

        # --- Fontes e observações finais (rescisão) ---
        st.markdown("### Fontes / Observações")
        st.markdown("- Cálculos baseados em regras gerais da CLT e nas alíquotas progressivas de INSS e IR (tabelas usuais).")
        st.markdown("- FGTS e multa de 40% são apresentados mas **não compõem** a base de cálculo do IR/INSS (situação padrão).")
        st.markdown("- Verifique situações específicas com orientador jurídico/contábil quando houver dúvidas (aviso trabalhado, descontos legais, acordos).")
