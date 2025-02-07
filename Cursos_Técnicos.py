import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)
def wide_space_default():
    st.set_page_config(layout='wide')

wide_space_default()

st.markdown("# Instituto Federal do Espírito Santo")
st.markdown("### Dados Históricos do cursos Técnicos do IFES")



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

df = pd.read_excel("data/cand_vaga_unico.xlsx", sheet_name = 0, dtype={'Semestre': str})
                        
df['Candidatos por Vaga'] = (df['Inscritos'] / df['Vagas']).round(2)

df_editais = pd.read_excel("data/cand_vaga_unico.xlsx", sheet_name= 1, dtype={'Semestre': str})

df_editais['Semestre'] = pd.to_datetime(df_editais['Semestre'])
df_editais['Semestre'] = df_editais['Semestre'].apply(lambda x: f"{x.year}/{1 if x.month <= 6 else 2}")

# st.dataframe(df_editais)

# st.dataframe(df)

# df_merged = pd.merge(df, df_editais, on=['Semestre', 'Curso'], how='left')
# colunas_editais = ['Semestre', 'Edital', 'Link']  
# df_merged['Link'] = df_merged['Link'].apply(lambda x: f'<a href="{x}" target="_blank">{x}</a>')

# st.markdown(df_merged.to_html(escape=False, index=False), unsafe_allow_html=True)
# Exibindo o DataFrame com links clicáveis

st.sidebar.title('Os filtros estão aqui! ✅')

# with st.expander("Mostrar Dados Filtrados"):
#     st.markdown(df_merged.to_html(escape=False, index=False), unsafe_allow_html=True)

filtered = filter_dataframe(df)
with st.expander("Mostrar Dados Filtrados"):
    st.dataframe(filtered)

# df_merged = pd.merge(df, df_editais, on='Semestre', how='inner')
# df_editais_selecionado = df_merged[colunas_editais]
# df_merged1 = pd.merge(filtered, df_editais, on='Semestre', how='inner')
# with st.expander("Editais Disponíveis"):
#     st.dataframe(df_merged1)

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

# fig_1.add_trace(
#     go.Indicator(
#         value=total_inscritos,
#         gauge={"axis": {"visible": False}},
#         number={
#             "font.size": 20,  # Reduzindo o tamanho do número
#         },
#         title={
#             "text": "Total de Inscritos",
#             "font": {"size": 16},  # Reduzindo o tamanho do título
#         },
#     )
# )

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

fig_6.add_trace(go.Bar(x=filtered['Semestre'], y=filtered['Candidatos por Vaga'], name='Candidato por Vaga'))

fig_6.update_layout(
    title='Tendência de Candidatos por Vaga',
    barmode='group',
    xaxis_tickangle=-45,
    # xaxis_title='Semestre',
    # yaxis_title='Quantidade',
    legend=dict(
        x=0,
        y=1.0) 
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
        size=filtered['Candidatos por Vaga'] * 5,
        sizemode='area',
        sizeref=2.*max(filtered['Candidatos por Vaga'])/(40.**2),
        color=filtered['Candidatos por Vaga'],
        colorscale='Viridis',
        colorbar=dict(title='Candidatos por Vaga')
    ),
    text=filtered['Semestre'],
    customdata=filtered[['Curso']],
    hovertemplate=
        '<b>Curso:</b> %{customdata[0]}<br>'+
        '<b>Semestre:</b> %{text}<br>'+
        '<b>Inscritos:</b> %{y}<br>'+
        '<b>Vagas:</b> %{x}<br>'+
        '<b>Candidatos por Vaga:</b> %{marker.color:.2f}<extra></extra>'
))

# Linha de tendência
z = np.polyfit(filtered['Vagas'], filtered['Inscritos'], 1)
p = np.poly1d(z)
fig_8.add_trace(go.Scatter(
    x=filtered['Vagas'],
    y=p(filtered['Vagas']),
    mode='lines',
    name='Tendência',
    line=dict(color='red', dash='dash')
))

# Layout final
fig_8.update_layout(
    title='Relação entre Inscritos e Vagas Ofertadas por Semestre',
    xaxis_title='Vagas Ofertadas',
    yaxis_title='Número de Inscritos',
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(size=14)
)

fig_9 = go.Figure()


fig_9.add_trace(go.Scatter(
    x=filtered['Semestre'], 
    y=filtered['Vagas'], 
    mode='lines+markers', 
    name='Vagas Ofertadas',
    line=dict(color='blue', width=2),
    marker=dict(size=5)
))

# Inscritos (linha verde)
fig_9.add_trace(go.Scatter(
    x=filtered['Semestre'], 
    y=filtered['Inscritos'], 
    mode='lines+markers', 
    name='Inscritos',
    line=dict(color='green', width=2),
    marker=dict(size=5)
))

# Candidatos por Vaga (linha vermelha com eixo secundário)
fig_9.add_trace(go.Scatter(
    x=filtered['Semestre'], 
    y=filtered['Candidatos por Vaga'], 
    mode='lines+markers', 
    name='Candidatos por Vaga',
    line=dict(color='red', width=2, dash='dot'),
    yaxis='y2',  # Define que essa série usa o eixo secundário
    marker=dict(size=5)
))

# Configuração do layout
fig_9.update_layout(
    title='Tendência das Vagas Ofertadas, Inscritos e Candidatos por Vaga',
    xaxis=dict(
        title='Semestre',
        tickangle=-45
    ),
    yaxis=dict(
        title='Vagas e Inscritos'
    ),
    yaxis2=dict(
        title='Candidatos por Vaga',
        overlaying='y',
        side='right',
        showgrid=False  # Remove grid do eixo secundário
    ),
    legend=dict(
        x=0.01,
        y=0.99,
        bgcolor='rgba(255,255,255,0.5)',
        bordercolor='black',
        borderwidth=1
    ),
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)'
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
