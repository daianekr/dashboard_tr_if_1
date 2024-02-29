import streamlit as st
import pandas as pd
import plotly.express as px

# Configurar o layout da página
st.set_page_config(layout="wide")

# Carregar os dados do arquivo "vendas.csv" (certifique-se de que o arquivo está no mesmo diretório)
df = pd.read_csv("matricula_teste.csv", sep=";")