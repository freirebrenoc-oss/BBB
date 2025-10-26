import pandas as pd

df = pd.read_csv(
    "BD_Consolidado_JF_Secao_23_Set_2025.csv",
    sep=';',       # ou ',' dependendo do seu CSV
    encoding='utf-8'  # ou 'latin1'
)

# Limpar espaços e quebras de linha
df.columns = df.columns.str.strip().str.replace("\n", " ")

# Mostrar todas as colunas lidas
print(df.columns.tolist())
