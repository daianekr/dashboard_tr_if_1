from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objs as go
from streamlit_dynamic_filters import DynamicFilters
from streamlit_card import card


st.set_page_config(page_title="Scholar Analytics Dashboard", page_icon=":bar_chart:", layout="wide")

st.title("Scholar Analytics Dashboard")

st.markdown("_Protótipo v0.0.1_")

# st.markdown(
#     """
#     # Este é um teste de filtros! 🎮
#     """
# )

def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    modify = st.sidebar.checkbox("Adicionar Filtros")

    if not modify:
        return df

    df = df.copy()


    for col in df.columns:
        if is_object_dtype(df[col]):
            try:
                df[col] = pd.to_datetime(df[col])
            except Exception:
                pass

        if is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.tz_localize(None)

    modification_container = st.sidebar.container()

    with modification_container:
        to_filter_columns = st.multiselect("Filtrar pela Coluna: ", df.columns)
        for column in to_filter_columns:
            left, right = st.columns((1, 20))

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


df = pd.read_csv("Dados_2012_1_2023_1_DC.csv", sep=",")

df['Nome do Curso - Sem Código'] = df['Nome do Curso'].str.split(' - ').str[1]
df['Semestre de Início'] = df['Semestre Início'].str.replace('/1', 'º semestre de')
def month_delta(date1, date2):
    return (date1.year - date2.year) * 12 + date1.month - date2.month

df['Semestre Início'] = pd.to_datetime(df['Semestre Início'])
df['Semestre Fim'] = pd.to_datetime(df['Semestre Fim'])
df['Tempo no curso em Meses'] = df.apply(lambda row: month_delta(row['Semestre Fim'], row['Semestre Início']), axis=1)
# df['Tempo no curso em Meses'] = (df['Semestre Fim'].dt.to_period('M') - df['Semestre Início'].dt.to_period('M')).astype(int)

# Create a sidebar
st.sidebar.title('Seus filtros estão aqui! ✅')

# Add a card inside the sidebar
with st.sidebar:
    st.write("É possível aplicar quantos filtros quiser")   
    st.write("Os filtros são as colunas do DataFrame")


filtered = filter_dataframe(df)
with st.expander("Mostrar Dados Filtrados"):
    st.dataframe(filtered)

col1, col2 = st.columns(2) # Primeira linha com duas colunas
col3, col4 = st.columns(2) # Segunda linha com três colunas
col5, col6 = st.columns(2) # Terceira linha com três colunas





res = card(
    title="Streamlit Card",
    text=["This is a test card", "This is a subtext"]
)



fig_1 = go.Figure()

fig_1.add_trace(
    go.Indicator(
        value=filtered.count()[0],
        gauge={"axis": {"visible": False}},
        number={
            "font.size": 28,
        },
        title={
            "text": "Total de Alunos",
            "font": {"size": 24},
        },
    )
)

col1.plotly_chart(fig_1, use_container_width=True)

category_counts = filtered['Situação da Matrícula'].value_counts()


fig = go.Figure(data=[go.Bar(x=category_counts.index, y=category_counts.values)])


fig.update_layout(title='Total de Alunos por Situação da Matrícula')



col3.plotly_chart(fig, use_container_width=True)

count_instituicoes = filtered['Instituição'].value_counts()

fig1 = px.pie(count_instituicoes, values=count_instituicoes.values, names=count_instituicoes.index, title='Distribuição de Instituições',hole=.3)

col2.plotly_chart(fig1, use_container_width=True)


course_counts = filtered['Nome do Curso - Sem Código'].value_counts()

fig2 = go.Figure(data=[go.Bar(x=course_counts.index, y=course_counts.values)])


fig2.update_layout(title='Total de Alunos por Curso')

fig2.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)

col4.plotly_chart(fig2, use_container_width=True)

y_counts = filtered.loc[(filtered['Sexo']=='M')].groupby('Instituição').size().tolist()
z_counts = filtered.loc[(filtered['Sexo']=='F')].groupby('Instituição').size().tolist()

fig3 = go.Figure(
    data=[
        go.Bar(x=filtered['Instituição'], y=y_counts, name="Feminino"),
        go.Bar(x=filtered['Instituição'], y=z_counts, name="Masculino")
    ],
    layout=dict(
        barcornerradius=15,
    ),
)

col5.plotly_chart(fig3, use_container_width=True)






# Lista para armazenar os gráficos de barras

# dynamic_filters = DynamicFilters(df=df, filters=['Instituicao', 'Descricao_Curso','Semestre_Ini','Semestre_fim'])
                                 
# dynamic_filters.display_filters(location='sidebar')
# dynamic_filters.display_df()                            

# initial_sem = st.sidebar.selectbox("Selecione o Peródo de Início", df["Semestre_Ini"].unique())

# df_filtered = df[df["Semestre_Ini"] == initial_sem]

# # Exibir o DataFrame filtrado
# st.write(df_filtered)
