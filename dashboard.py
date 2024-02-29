from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)
import pandas as pd
import streamlit as st
import plotly.express as px
from streamlit_dynamic_filters import DynamicFilters
import plotly.graph_objs as go

# Configurar o layout da página
st.set_page_config(layout="wide")
st.title("Isto é um teste de Filtros!")

def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a UI on top of a dataframe to let viewers filter columns

    Args:
        df (pd.DataFrame): Original dataframe

    Returns:
        pd.DataFrame: Filtered dataframe
    """
    modify = st.checkbox("Adicionar Filtros")

    if not modify:
        return df

    df = df.copy()

    # Try to convert datetimes into a standard format (datetime, no timezone)
    for col in df.columns:
        if is_object_dtype(df[col]):
            try:
                df[col] = pd.to_datetime(df[col])
            except Exception:
                pass

        if is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.tz_localize(None)

    modification_container = st.container()

    with modification_container:
        to_filter_columns = st.multiselect("Filtrar pela Coluna: ", df.columns)
        for column in to_filter_columns:
            left, right = st.columns((1, 20))
            # Treat columns with < 10 unique values as categorical
            if is_categorical_dtype(df[column]) or df[column].nunique() < 10:
                user_cat_input = right.multiselect(
                    f"Values for {column}",
                    df[column].unique(),
                    default=list(df[column].unique()),
                )
                df = df[df[column].isin(user_cat_input)]
            elif is_numeric_dtype(df[column]):
                _min = float(df[column].min())
                _max = float(df[column].max())
                step = (_max - _min) / 100
                user_num_input = right.slider(
                    f"Values for {column}",
                    min_value=_min,
                    max_value=_max,
                    value=(_min, _max),
                    step=step,
                )
                df = df[df[column].between(*user_num_input)]
            elif is_datetime64_any_dtype(df[column]):
                user_date_input = right.date_input(
                    f"Values for {column}",
                    value=(
                        df[column].min(),
                        df[column].max(),
                    ),
                )
                if len(user_date_input) == 2:
                    user_date_input = tuple(map(pd.to_datetime, user_date_input))
                    start_date, end_date = user_date_input
                    df = df.loc[df[column].between(start_date, end_date)]
            else:
                user_text_input = right.text_input(
                    f"Digite uma substring pelo que quer filtrar de {column}",
                )
                if user_text_input:
                    df = df[df[column].astype(str).str.contains(user_text_input)]

    return df


# Carregar os dados do arquivo "vendas.csv" (certifique-se de que o arquivo está no mesmo diretório)
df = pd.read_csv("Dados_2012_1_2023_1_DC.csv", sep=",")

filtered = filter_dataframe(df)

st.dataframe(filtered)

col1, col2 = st.columns(2) # Primeira linha com duas colunas
col3, col4, col5 = st.columns(3) # Segunda linha com três colunas

# Count the occurrences of each category
category_counts = filtered['Situação da Matrícula'].value_counts()

# Create the Plotly bar chart
fig = go.Figure(data=[go.Bar(x=category_counts.index, y=category_counts.values)])

# Update layout
fig.update_layout(title='Contagem por Situação da Matrícula',
                  xaxis_title='Situação da Matrícula',
                  yaxis_title='Contagem de Alunos')


# Exibir o gráfico na primeira coluna
col1.plotly_chart(fig, use_container_width=True)

# dynamic_filters = DynamicFilters(df=df, filters=['Instituicao', 'Descricao_Curso','Semestre_Ini','Semestre_fim'])
                                 
# dynamic_filters.display_filters(location='sidebar')
# dynamic_filters.display_df()                            

# initial_sem = st.sidebar.selectbox("Selecione o Peródo de Início", df["Semestre_Ini"].unique())

# df_filtered = df[df["Semestre_Ini"] == initial_sem]

# # Exibir o DataFrame filtrado
# st.write(df_filtered)
