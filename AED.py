import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# Dados baseados no teste regulatório
dados = {
    "Mês": ["jun/24", "jul/24", "ago/24", "set/24", "out/24"],
    "Taxa de inadimplência (%)": [6.5, 7.2, 8.0, 9.1, 8.5],
    "Benefício líquido do Free Flow (%)": [4, 5.5, 6.8, 8.2, 9.5]
}

df = pd.DataFrame(dados)

# Layout da página
st.title("Efeitos da Regulação Inteligente da ANTT sobre o Modelo Free Flow")
st.markdown("""
Este gráfico demonstra que, embora a **inadimplência** apresente crescimento inicial no sistema de pedágio eletrônico (*Free Flow*),
a **regulação inteligente da ANTT** — por meio do *sandbox regulatório* e do ajuste do prazo de pagamento — 
gera **eficiência líquida positiva**, mostrando que os **benefícios superam os custos de enforcement**.
""")

# Criação do gráfico
fig = go.Figure()

# Linha da inadimplência
fig.add_trace(go.Scatter(
    x=df["Mês"],
    y=df["Taxa de inadimplência (%)"],
    mode="lines+markers",
    name="Taxa de Inadimplência",
    line=dict(color="red", width=3),
    marker=dict(size=8)
))

# Linha dos benefícios líquidos
fig.add_trace(go.Scatter(
    x=df["Mês"],
    y=df["Benefício líquido do Free Flow (%)"],
    mode="lines+markers",
    name="Benefício Líquido (eficiência)",
    line=dict(color="green", width=3, dash="dash"),
    marker=dict(size=8)
))

# Linha de compensação visual
fig.add_hline(y=8.03, line_dash="dot", line_color="gray",
              annotation_text="Média de inadimplência no período (8,03%)",
              annotation_position="bottom right")

fig.update_layout(
    title="Free Flow: os benefícios superam os custos de enforcement",
    xaxis_title="Período (2024)",
    yaxis_title="Percentual (%)",
    legend_title="Indicadores",
    template="plotly_white",
    font=dict(size=14)
)

# Comentário interpretativo
st.plotly_chart(fig)

st.markdown("""
📊 **Análise:**  
- A **linha vermelha** mostra o aumento temporário da inadimplência (até 9,1% em setembro).  
- A **linha verde** mostra o crescimento do **benefício líquido**, que supera os 9% ao final do período.  
- Isso demonstra que, ao ajustar o prazo de pagamento e aprimorar os mecanismos de cobrança, 
a **ANTT converteu aprendizado regulatório em eficiência econômica**, reduzindo os custos de transação 
associados ao pluralismo institucional.  

✅ **Conclusão:** mesmo com inadimplência moderada, o **Free Flow permanece vantajoso**.  
A regulação eficiente transforma o risco de inadimplência em um **custo de transição**, não estrutural.
""")
