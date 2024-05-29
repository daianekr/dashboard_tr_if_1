import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)

st.markdown("# Dashboard IFES 🎈")
st.sidebar.markdown("# Página Principal dos dashboards 🎈")
st.markdown("## Dados Históricos do cursos Técnicos do IFES")

def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    modify = st.sidebar.checkbox("Adicionar Filtros")

    if not modify:
        return df

    df = df.copy()

    for col in df.columns:
        # Verifica se a coluna parece representar datas antes de tentar converter
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


df = pd.read_csv("data/Dados.csv", sep=';', encoding='latin1')

st.sidebar.title('Seus filtros estão aqui! ✅')

with st.sidebar:
    st.write("É possível aplicar quantos filtros quiser")   
    st.write("Os filtros são as colunas do DataFrame")


filtered = filter_dataframe(df)
with st.expander("Mostrar Dados Filtrados"):
    st.dataframe(filtered)

total_matriculas = filtered.shape[0]
media_reprovacoes = filtered['Quant_Rep'].mean()
total_cursos = filtered['Curso'].nunique()
# tempo_medio = filtered['Tempo'].mean()
distrib_sexo = filtered['Sexo'].value_counts()

col1, col2, col3, col4 = st.columns(4) 
col5 = st.columns(1) 
col6 = st.columns(1)
col7 = st.columns(1)
col8 = st.columns(1)
col9 = st.columns(1)
col10 = st.columns(1)
col11 = st.columns(1)
col12 = st.columns(1)

fig_1 = go.Figure()

fig_1.add_trace(
    go.Indicator(
        value=total_matriculas,
        gauge={"axis": {"visible": False}},
        number={
            "font.size": 28,
        },
        title={
            "text": "Total de Inscritos",
            "font": {"size": 24},
        },
    )
)

fig_2 = go.Figure()

fig_2.add_trace(
    go.Indicator(
        value=media_reprovacoes,
        gauge={"axis": {"visible": False}},
        number={
            "font.size": 28,
        },
        title={
            "text": "Média de Reprovações",
            "font": {"size": 24},
        },
    )
)

fig_3 = go.Figure()


fig_3.add_trace(
    go.Indicator(
        value=total_cursos,
        gauge={"axis": {"visible": False}},
        number={
            "font.size": 28,
        },
        title={
            "text": "Total de Cursos",
            "font": {"size": 24},
        },
    )
)

fig_4 = go.Figure()

fig_4.add_trace(
    go.Indicator(
        value=total_matriculas,
        gauge={"axis": {"visible": False}},
        number={
            "font.size": 28,
        },
        title={
            "text": "A definir",
            "font": {"size": 24},
        },
    )
)

fig_5 = go.Figure()
fig_5.add_trace(go.Bar(x=filtered['Curso'].value_counts().index, y=filtered['Curso'].value_counts().values, name='Curso'))

fig_5.update_layout(
    title='Número de Matrículas por Curso',
    # xaxis_title='Curso',
    # yaxis_title='Quantidade de Matrículas',
    xaxis_tickangle=-45
)

fig_6 = go.Figure()
fig_6.add_trace(go.Bar(x=filtered['Forma_Ingresso'].value_counts().index, y=filtered['Forma_Ingresso'].value_counts().values, name='Forma de Ingresso'))

fig_6.update_layout(
    title='Número de Matrículas por Forma de Ingresso',
    # xaxis_title='Forma de Ingresso',
    # yaxis_title='Quantidade de Matrículas',
    xaxis_tickangle=0
)

reprovações_por_curso = filtered.groupby('Curso')['Quant_Rep'].sum().reset_index()

fig_7 = go.Figure()
fig_7.add_trace(go.Bar(x=reprovações_por_curso['Curso'], y=reprovações_por_curso['Quant_Rep'], name='Reprovações'))

fig_7.update_layout(
    title='Quantidade de Reprovações por Curso',
    # xaxis_title='Curso',
    # yaxis_title='Quantidade de Reprovações',
    xaxis_tickangle=-45
)

df_grouped = filtered.groupby(['Semestre_Ini', 'Situacao_Matricula']).size().reset_index(name='Contagem')
df_pivot = df_grouped.pivot(index='Semestre_Ini', columns='Situacao_Matricula', values='Contagem').fillna(0)

fig_8 = go.Figure()
for situacao in df_pivot.columns:
    fig_8.add_trace(go.Scatter(x=df_pivot.index, y=df_pivot[situacao], mode='lines+markers', name=situacao))

fig_8.update_layout(
    title='Evolução da Situação de Matrícula ao Longo dos Semestres',
    # xaxis_title='Semestre de Início',
    # yaxis_title='Quantidade de Estudantes',
    xaxis_tickangle=-45,
    legend=dict(x=0, y=1.0)
)

fig_9 = go.Figure()
fig_9.add_trace(go.Pie(labels=filtered['Modalidade'].value_counts().index, values=filtered['Modalidade'].value_counts().values, name='Modalidade'))

fig_9.update_layout(
    title='Distribuição de Matrículas por Modalidade'
)

fig_10 = go.Figure()
fig_10.add_trace(go.Pie(labels=filtered['Sexo'].value_counts().index, values=filtered['Sexo'].value_counts().values, name='Sexo'))

fig_10.update_layout(
    title='Distribuição de Matrículas por Sexo'
)

df_grouped_ingresso_situacao = filtered.groupby(['Forma_Ingresso', 'Situacao_Matricula']).size().reset_index(name='Contagem')
df_pivot_ingresso_situacao = df_grouped_ingresso_situacao.pivot(index='Forma_Ingresso', columns='Situacao_Matricula', values='Contagem').fillna(0)

fig_11 = go.Figure()
for situacao in df_pivot_ingresso_situacao.columns:
    fig_11.add_trace(go.Bar(x=df_pivot_ingresso_situacao.index, y=df_pivot_ingresso_situacao[situacao], name=situacao))

fig_11.update_layout(
    title='Distribuição da Situação de Matrícula por Forma de Ingresso',
    # xaxis_title='Forma de Ingresso',
    # yaxis_title='Quantidade de Estudantes',
    barmode='stack',
    xaxis_tickangle=0,
    legend=dict(x=0, y=1.0)
)

fig_12 = go.Figure()

fig_12.add_trace(go.Scatter(x=filtered['Tempo'], y=filtered['Quant_Rep'], mode='markers', name='Tempo vs. Reprovações'))

fig_12.update_layout(
    title='Tempo no Curso vs. Quantidade de Reprovações',
    xaxis_title='Tempo no Curso (em semestres)',
    # yaxis_title='Quantidade de Reprovações'
)

col1.plotly_chart(fig_1, use_container_width=True)
col2.plotly_chart(fig_2, use_container_width=True)
col3.plotly_chart(fig_3, use_container_width=True)
col4.plotly_chart(fig_4, use_container_width=True)

with col5[0]:
    st.plotly_chart(fig_5, use_container_width=True)

with col6[0]:
    st.plotly_chart(fig_6, use_container_width=True)
    
with col7[0]:
    st.plotly_chart(fig_7, use_container_width=True)
    
with col8[0]:
    st.plotly_chart(fig_8, use_container_width=True)

with col9[0]:
    st.plotly_chart(fig_9, use_container_width=True)

with col10[0]:
    st.plotly_chart(fig_10, use_container_width=True)

with col11[0]:
    st.plotly_chart(fig_11, use_container_width=True)

with col12[0]:
    st.plotly_chart(fig_12, use_container_width=True)

