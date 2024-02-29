import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_dynamic_filters import DynamicFilters

# Configurar o layout da página
st.set_page_config(layout="wide")
st.title("Isto é um teste de Filtros!")

# Carregar os dados do arquivo "vendas.csv" (certifique-se de que o arquivo está no mesmo diretório)
df = pd.read_csv("Dados_2012_1_2023_1_DC.csv", sep=",")

dynamic_filters = DynamicFilters(df=df, filters=['Instituicao', 'Descricao_Curso','Semestre_Ini','Semestre_fim'])
                                 
dynamic_filters.display_filters(location='sidebar')
dynamic_filters.display_df()                            

# initial_sem = st.sidebar.selectbox("Selecione o Peródo de Início", df["Semestre_Ini"].unique())

# df_filtered = df[df["Semestre_Ini"] == initial_sem]

# # Exibir o DataFrame filtrado
# st.write(df_filtered)
