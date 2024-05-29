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



df = pd.read_excel("data/cand_vaga_unico.xlsx", sheet_name = 0, dtype={'Semestre': str}
                        )
df['Candidatos por Vaga'] =(df['Inscritos'] / df['Vagas']).round(2)
df_editais = pd.read_excel("data/cand_vaga_unico.xlsx", sheet_name= 1, dtype={'Semestre': str})
df_merged = pd.merge(df, df_editais, on='Semestre', how='inner')
colunas_editais = ['Semestre', 'Edital', 'Link']  


st.sidebar.title('Seus filtros estão aqui! ✅')

with st.sidebar:
    st.write("É possível aplicar quantos filtros quiser")   
    st.write("Os filtros são as colunas do DataFrame")


filtered = filter_dataframe(df)
with st.expander("Mostrar Dados Filtrados"):
    st.dataframe(filtered)

df_merged = pd.merge(df, df_editais, on='Semestre', how='inner')
df_editais_selecionado = df_merged[colunas_editais]
with st.expander("Editais Disponíveis"):
    st.dataframe(df_merged)

col1, col2, col3, col4 = st.columns(4) 
col5 = st.columns(1) 
col6 = st.columns(1)
col7 = st.columns(1)
col8 = st.columns(1)
col9 = st.columns(1)

total_inscritos = filtered['Inscritos'].sum()
total_vagas = filtered['Vagas'].sum()
total_cursos = filtered['Curso'].nunique()
cadidato_vaga = filtered['Inscritos'].sum() / filtered['Vagas'].sum()
cores_personalizadas = ['#ffaec8', '#87ceeb']

fig_1 = go.Figure()

fig_1.add_trace(
    go.Indicator(
        value=total_inscritos,
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
        value=total_vagas,
        gauge={"axis": {"visible": False}},
        number={
            "font.size": 28,
        },
        title={
            "text": "Vagas Ofertadas",
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
        value=cadidato_vaga,
        gauge={"axis": {"visible": False}},
        number={
            "font.size": 28,
        },
        title={
            "text": "Candidatos por Vaga",
            "font": {"size": 24},
        },
    )
)

fig_5 = go.Figure()
fig_5.add_trace(go.Bar(x=filtered['Semestre'], y=filtered['Vagas'], name='Vagas Ofertadas'))
fig_5.add_trace(go.Bar(x=filtered['Semestre'], y=filtered['Inscritos'], name='Inscritos'))

fig_5.update_layout(
    title='Vagas Ofertadas e Inscritos por Semestre',
    # xaxis_title='Semestre',
    # yaxis_title='Quantidade',
    barmode='group',
    xaxis_tickangle=-45,
    legend=dict(
        x=0,
        y=1.0) 
)

fig_6 = go.Figure()

fig_6.add_trace(go.Scatter(x=filtered['Semestre'], y=filtered['Candidatos por Vaga'], mode='lines', fill='tozeroy', name='Candidato por Vaga', text=['Candidato por Vaga']))

fig_6.update_layout(
    title='Tendência de Candidatos por Vaga',
    xaxis_tickangle=-45,
    # xaxis_title='Semestre',
    # yaxis_title='Quantidade',
)



fig_7 = go.Figure()

# Adicionando as barras para as vagas ofertadas e inscritos
fig_7.add_trace(go.Bar(x=filtered['Semestre'], y=filtered['Vagas'], name='Vagas Ofertadas'))
fig_7.add_trace(go.Bar(x=filtered['Semestre'], y=filtered['Inscritos'], name='Inscritos'))


fig_7.update_layout(
    title='Distribuição de Vagas e Inscritos por Semestre',
    # xaxis_title='Semestre',
    # yaxis_title='Quantidade',
    barmode='stack',
    xaxis_tickangle=-45,
    legend=dict(
        x=0,
        y=1.0) 
)

fig_8 = go.Figure()

fig_8.add_trace(go.Scatter(
    x=filtered['Vagas'],
    y=filtered['Inscritos'],
    mode='markers',  
    marker=dict(
        size=filtered['Candidatos por Vaga'],  
        color=filtered['Candidatos por Vaga'],  
        colorscale='Viridis',  
        colorbar=dict(title='Candidatos por Vaga'),  
    ),
    text=filtered['Semestre'], 
))


fig_8.update_layout(
    title='Relação entre Inscritos e Vagas Ofertadas por Semestre',
    # xaxis_title='Vagas Ofertadas',
    # yaxis_title='Inscritos',
)

fig_9 = go.Figure()


fig_9.add_trace(go.Scatter(x=filtered['Semestre'], y=filtered['Vagas'], mode='lines+markers', name='Vagas Ofertadas'))
fig_9.add_trace(go.Scatter(x=filtered['Semestre'], y=filtered['Inscritos'], mode='lines+markers', name='Inscritos'))


fig_9.add_trace(go.Scatter(x=filtered['Semestre'], y=filtered['Candidatos por Vaga'], mode='lines', fill='tozeroy', name='Candidato por Vaga'))


fig_9.update_layout(
    title='Tendência das Vagas Ofertadas, Inscritos e Candidato por Vaga',
    # xaxis_title='Semestre',
    # yaxis_title='Quantidade',
    xaxis_tickangle=-45,
    legend=dict(
        x=0,
        y=1.0) 
)

col1.plotly_chart(fig_1, use_container_width=True)
col2.plotly_chart(fig_2, use_container_width=True)
col3.plotly_chart(fig_3, use_container_width=True)
col4.plotly_chart(fig_4, use_container_width=True)

with col5[0]:
    st.plotly_chart(fig_5, use_container_width=True)
# col5.plotly_chart(fig_5, use_container_width=True)
with col6[0]:
    st.plotly_chart(fig_6, use_container_width=True)
# col6.plotly_chart(fig_6, use_container_width=True)
    
with col7[0]:
    st.plotly_chart(fig_7, use_container_width=True)
# col7.plotly_chart(fig_7, use_container_width=True)
    
with col8[0]:
    st.plotly_chart(fig_8, use_container_width=True)
# col8.plotly_chart(fig_8, use_container_width=True)

with col9[0]:
    st.plotly_chart(fig_9, use_container_width=True)
