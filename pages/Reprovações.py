import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)

st.markdown("# Dados de Reprovações")

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

df = pd.read_csv('data/Reprovacoes.csv', sep=';', encoding='utf-8') 
st.sidebar.title('Seus filtros estão aqui! ✅')

filtered = filter_dataframe(df)
with st.expander("Mostrar Dados Filtrados"):
    st.dataframe(filtered)

col1, col2, col3, col4 = st.columns(4)
col5, = st.columns(1)
col6, = st.columns(1)
col7, = st.columns(1)
col8, = st.columns(1)
col9, = st.columns(1)
col10, = st.columns(1)
col11, = st.columns(1)
col12, = st.columns(1)


filtro_alunos = filtered['Matrícula (Anom)'].unique()
soma_valores_distintos = len(filtro_alunos)
fig_1 = go.Figure()

fig_1.add_trace(
    go.Indicator(
        value=soma_valores_distintos,
        gauge={"axis": {"visible": False}},
        number={
            "font.size": 28,
        },
        title={
            "text": "Total de Matrículas",
            "font": {"size": 24},
        },
    )
)

fig_2 = go.Figure()

fig_2.add_trace(
    go.Indicator(
        value=soma_valores_distintos,
        gauge={"axis": {"visible": False}},
        number={
            "font.size": 28,
        },
        title={
            "text": "Total de Matrículas",
            "font": {"size": 24},
        },
    )
)


fig_3 = go.Figure()

fig_3.add_trace(
    go.Indicator(
        value=soma_valores_distintos,
        gauge={"axis": {"visible": False}},
        number={
            "font.size": 28,
        },
        title={
            "text": "Total de Matrículas",
            "font": {"size": 24},
        },
    )
)


fig_4 = go.Figure()

fig_4.add_trace(
    go.Indicator(
        value=soma_valores_distintos,
        gauge={"axis": {"visible": False}},
        number={
            "font.size": 28,
        },
        title={
            "text": "Total de Matrículas",
            "font": {"size": 24},
        },
    )
)



fig_5 = go.Figure()
fig_5.add_trace(go.Bar(x=df['Campus'].value_counts().index, y=df['Campus'].value_counts().values, name='Campus'))

fig_5.update_layout(
    title='Distribuição de Estudantes por Campus',
    # xaxis_title='Campus',
    # yaxis_title='Quantidade de Estudantes',
    xaxis_tickangle=-45
)


fig_6 = go.Figure()
fig_6.add_trace(go.Pie(labels=df['Modalidade'].value_counts().index, values=df['Modalidade'].value_counts().values, name='Modalidade'))

fig_6.update_layout(
    title='Distribuição de Estudantes por Modalidade'
)

fig_7 = go.Figure()
fig_7.add_trace(go.Bar(x=df['Situação Matrícula'].value_counts().index, y=df['Situação Matrícula'].value_counts().values, name='Situação Matrícula'))

fig_7.update_layout(
    title='Desempenho dos Estudantes',
    # xaxis_title='Situação da Matrícula',
    # yaxis_title='Quantidade de Estudantes',
    xaxis_tickangle=-45
)

fig_8 = go.Figure()
fig_8.add_trace(go.Histogram(x=df['Quantidade de Reprovações'], name='Reprovações'))

fig_8.update_layout(
    title='Distribuição da Quantidade de Reprovações',
    # xaxis_title='Quantidade de Reprovações',
    # yaxis_title='Contagem de Estudantes'
)


df_evolucao = filtered.groupby('Semestre Início').size().reset_index(name='Contagem')

fig_9 = go.Figure()
fig_9.add_trace(go.Scatter(x=df_evolucao['Semestre Início'], y=df_evolucao['Contagem'], mode='lines+markers', name='Matrículas'))

fig_9.update_layout(
    title='Evolução do Número de Estudantes ao Longo dos Semestres',
    # xaxis_title='Semestre Início',
    # yaxis_title='Quantidade de Matrículas',
    xaxis_tickangle=-45
)

df_grouped = filtered.groupby(['Semestre Início', 'Situação Matrícula']).size().reset_index(name='Contagem')
df_pivot = df_grouped.pivot(index='Semestre Início', columns='Situação Matrícula', values='Contagem').fillna(0)


fig_10 = go.Figure()

for situacao in df_pivot.columns:
    fig_10.add_trace(go.Scatter(x=df_pivot.index, y=df_pivot[situacao], mode='lines+markers', name=situacao))

fig_10.update_layout(
    title='Evolução das Situações de Matrícula ao Longo dos Semestres',
    # xaxis_title='Semestre Início',
    # yaxis_title='Quantidade de Estudantes',
    xaxis_tickangle=-45,
    legend=dict(x=0, y=1.0)
)

df_agrupado = filtered.groupby(['Forma Ingresso', 'Situação Matrícula']).size().reset_index(name='Contagem')


df_pivot_1 = df_agrupado.pivot(index='Forma Ingresso', columns='Situação Matrícula', values='Contagem').fillna(0)

fig_11 = go.Figure()

for situacao in df_pivot_1.columns:
    fig_11.add_trace(go.Bar(
        x=df_pivot_1.index,
        y=df_pivot_1[situacao],
        name=situacao
    ))

fig_11.update_layout(
    title='Distribuição da Situação de Matrícula por Forma de Ingresso',
    # xaxis_title='Forma de Ingresso',
    # yaxis_title='Quantidade de Estudantes',
    barmode='stack',
    xaxis_tickangle=-45,
    legend=dict(x=0, y=1.0)
)

fig_12 = go.Figure()

for situacao in df_pivot.columns:
    fig_12.add_trace(go.Bar(
        x=df_pivot_1.index,
        y=df_pivot_1[situacao],
        name=situacao
    ))

fig_12.update_layout(
    title='Distribuição da Situação de Matrícula por Forma de Ingresso',
    xaxis_title='Forma de Ingresso',
    yaxis_title='Quantidade de Estudantes',
    barmode='group',
    xaxis_tickangle=-45,
    legend=dict(x=0, y=1.0)
)




# col5.plotly_chart(fig_5, use_container_width=True)
# col6.plotly_chart(fig_6, use_container_width=True)
# col7.plotly_chart(fig_7, use_container_width=True)
# col8.plotly_chart(fig_8, use_container_width=True)
# col9.plotly_chart(fig_9, use_container_width=True)
# col10.plotly_chart(fig_10, use_container_width=True)
# col11.plotly_chart(fig_11, use_container_width=True)
# col12.plotly_chart(fig_12, use_container_width=True)


with col5:
    st.plotly_chart(fig_5, use_container_width=True)

with col6:
    st.plotly_chart(fig_6, use_container_width=True)
    
with col7:
    st.plotly_chart(fig_7, use_container_width=True)
    
with col8:
    st.plotly_chart(fig_8, use_container_width=True)

with col9:
    st.plotly_chart(fig_9, use_container_width=True)

with col10:
    st.plotly_chart(fig_10, use_container_width=True)

with col11:
    st.plotly_chart(fig_11, use_container_width=True)

with col12:
    st.plotly_chart(fig_12, use_container_width=True)