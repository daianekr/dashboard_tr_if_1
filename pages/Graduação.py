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

st.set_page_config(page_title="Dados Graduação", page_icon=":bar_chart:", layout="wide")
st.markdown("# Dados Graduação")
st.sidebar.markdown("# Dados Graduação")


st.markdown("### Relatório Analítico Escolar")

st.markdown("_Protótipo v0.0.1_")

@st.cache_data(show_spinner=False)
def load_data(file_path,sep):
    dataset = pd.read_csv(file_path,sep=sep)
    return dataset

df = load_data("data/Dados_2012_1_2023_1_DC.csv", sep=",")


# st.markdown(
#     # """
#     # # Este é um teste de filtros! 🎮
#     # """
# )

def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    modify = st.sidebar.checkbox("Adicionar Filtros")

    if not modify:
        return df

    df = df.copy()

    for col in df.columns:
        if is_object_dtype(df[col]) and df[col].str.contains(r'\d{4}/\d{2}').all():
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

            if isinstance(df[column].dtype, pd.CategoricalDtype) or df[column].nunique() < 10:
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




df['Nome do Curso - Sem Código'] = df['Nome do Curso'].str.split(' - ').str[1]
# df['Semestre de Início'] = df['Semestre Início'].str.replace('/1', 'º semestre de')
# def month_delta(date1, date2):
#     return (date1.year - date2.year) * 12 + date1.month - date2.month

# df['Semestre Início'] = pd.to_datetime(df['Semestre Início'])
# df['Semestre Fim'] = pd.to_datetime(df['Semestre Fim'])
# df['Tempo no curso em Meses'] = df.apply(lambda row: month_delta(row['Semestre Fim'], row['Semestre Início']), axis=1)
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

@st.cache_data(show_spinner=False)
def split_frame(input_df, rows):
    df = [input_df.loc[i : i + rows - 1, :] for i in range(0, len(input_df), rows)]
    return df

top_menu = st.columns(3)
with top_menu[0]:
    sort = st.radio("Ordenar dados? ", options=["Sim", "Não"], horizontal=1, index=1)
if sort == "Sim":
    with top_menu[1]:
        sort_field = st.selectbox("Ordernar por", options=filtered.columns)
    with top_menu[2]:
        sort_direction = st.radio(
            "Direção", options=["⬆️", "⬇️"], horizontal=True
        )
    filtered = filtered.sort_values(
        by=sort_field, ascending=sort_direction == "⬆️", ignore_index=True
    )
pagination = st.container()

bottom_menu = st.columns((4, 1, 1))
with bottom_menu[2]:
    batch_size = st.selectbox("Itens por Página", options=[25, 50, 100])
with bottom_menu[1]:
    total_pages = (
        int(len(filtered) / batch_size) if int(len(filtered) / batch_size) > 0 else 1
    )
    current_page = st.number_input(
        "Página", min_value=1, max_value=total_pages, step=1
    )
with bottom_menu[0]:
    st.markdown(f"Página **{current_page}** de **{total_pages}** ")

pages = split_frame(filtered, batch_size)
pagination.dataframe(data=pages[current_page - 1], use_container_width=True)

col1, col2, col3, col4 = st.columns(4) 
col5 = st.columns(1) 
col6 = st.columns(1) 
col7 = st.columns(1) 

total_matriculas_acao_afirmativa = (filtered['Forma de Ingresso'] == 'Ação Afirmativa').sum()
total_matriculas_ampla_concorrencia = (filtered['Forma de Ingresso'] == 'Ampla Concorrência').sum()
total_matriculas_outra = (filtered['Forma de Ingresso'] == 'Outro').sum()

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

fig_2 = go.Figure()

fig_2.add_trace(
    go.Indicator(
        value=total_matriculas_acao_afirmativa,
        gauge={"axis": {"visible": False}},
        number={
            "font.size": 28,
        },
        title={
            "text": "Ação Afirmativa",
            "font": {"size": 24},
        },
    )
)

col2.plotly_chart(fig_2, use_container_width=True)

fig_3 = go.Figure()

fig_3.add_trace(
    go.Indicator(
        value=total_matriculas_ampla_concorrencia,
        gauge={"axis": {"visible": False}},
        number={
            "font.size": 28,
        },
        title={
            "text": "Ampla Concorrência",
            "font": {"size": 24},
        },
    )
)

col3.plotly_chart(fig_3, use_container_width=True)

fig_4 = go.Figure()

fig_4.add_trace(
    go.Indicator(
        value=total_matriculas_outra,
        gauge={"axis": {"visible": False}},
        number={
            "font.size": 28,
        },
        title={
            "text": "Outro",
            "font": {"size": 24},
        },
    )
)

col4.plotly_chart(fig_4, use_container_width=True)

category_counts = filtered['Situação da Matrícula'].value_counts()

fig_5 = go.Figure(data=[go.Bar(x=category_counts.index, y=category_counts.values)])
fig_5.update_layout(title='Total de Alunos por Situação da Matrícula')

count_instituicoes = filtered['Instituição'].value_counts()

fig_5 = px.pie(count_instituicoes, values=count_instituicoes.values, names=count_instituicoes.index, title='Distribuição de Instituições',hole=.3)

course_counts = filtered['Nome do Curso - Sem Código'].value_counts()

fig_6 = go.Figure(data=[go.Bar(x=course_counts.index, y=course_counts.values)])
fig_6.update_layout(title='Total de Alunos por Curso', xaxis_tickangle=-45)
fig_6.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)

male_counts = filtered.loc[filtered['Sexo'] == 'M'].groupby('Instituição').size()
female_counts = filtered.loc[filtered['Sexo'] == 'F'].groupby('Instituição').size()

# Garantir que ambas as séries tenham o mesmo índice (instituições)
institutions = sorted(set(male_counts.index).union(set(female_counts.index)))

# Preencher com 0 onde não houver registros
male_counts = male_counts.reindex(institutions, fill_value=0)
female_counts = female_counts.reindex(institutions, fill_value=0)

# Criar o gráfico
fig_7 = go.Figure(
    data=[
        go.Bar(x=institutions, y=female_counts, name="Feminino", marker_color='rgb(255, 105, 180)'),  # Rosa para Feminino
        go.Bar(x=institutions, y=male_counts, name="Masculino", marker_color='rgb(65, 105, 225)'),   # Azul para Masculino
    ]
)

# Layout com cantos arredondados e ajustes de visualização
fig_7.update_layout(
    title='Distribuição de Matrículas por Instituição e Sexo',
    xaxis_title='Instituição',
    yaxis_title='Número de Matrículas',
    barmode='group',  # Barras lado a lado
    bargap=0.2,
    bargroupgap=0.1,
)

with col5[0]:
    st.plotly_chart(fig_5, use_container_width=True)

with col6[0]:
    st.plotly_chart(fig_6, use_container_width=True)

with col7[0]:
    st.plotly_chart(fig_7, use_container_width=True)



# incluir eficiência academica 

# Lista para armazenar os gráficos de barras

# dynamic_filters = DynamicFilters(df=df, filters=['Instituicao', 'Descricao_Curso','Semestre_Ini','Semestre_fim'])
                                 
# dynamic_filters.display_filters(location='sidebar')
# dynamic_filters.display_df()                            

# initial_sem = st.sidebar.selectbox("Selecione o Peródo de Início", df["Semestre_Ini"].unique())

# df_filtered = df[df["Semestre_Ini"] == initial_sem]

# # Exibir o DataFrame filtrado
# st.write(df_filtered)
