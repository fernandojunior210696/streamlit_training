from email import header
import streamlit as st
import pandas as pd
from gsheetsdb import connect
from IPython.core.display import HTML

import plotly.express as px
import plotly.graph_objects as go

# Título do dashboard
# st.title("Catálogo Woods Wine")
st.markdown("<h1 style='text-align: center; '>Catálogo Woods Wine</h1>", unsafe_allow_html=True)

st.sidebar.image('./images/logo_woods.png',use_column_width='always')

st.sidebar.write(" ")
st.sidebar.markdown("## Filtre abaixo por país, tipo de uva, faixa de preço ou pelo nome do vinho e faça sua escolha!")

@st.cache
def get_data(url):
    # Recupera dados da planilha do google sheets
    gsheet_url = url
    # gsheet_url = st.secrets["public_gsheets_url"]
    conn = connect()
    rows = conn.execute(f'SELECT NOME AS wine_name, TIPO AS grape_type, ORIGEM AS country, VALOR AS price, BANDEIRA AS flag  FROM "{gsheet_url}"')

    # Converte dados para pandas df
    df_gsheet = pd.DataFrame(rows)
    return df_gsheet

def path_to_image_html(path):
    '''
     This function essentially convert the image url to 
     '<img src="'+ path + '"/>' format. And one can put any
     formatting adjustments to control the height, aspect ratio, size etc.
     within as in the below example. 
    '''

    return '<img src="'+ path + '" style=max-height:24px;"/>'

df_gsheet = get_data(st.secrets["public_gsheets_url"])

values = st.sidebar.slider(label = "Preço dos vinhos", 
                           min_value = df_gsheet.price.min(), 
                           max_value = df_gsheet.price.max(),
                           value = (float(df_gsheet.price.min()), float(df_gsheet.price.max())))

# Selected price range
min_price=values[0]
max_price=values[1]

# Selected country
country = st.sidebar.selectbox("Selecione o país", ['selecione'] + list(df_gsheet.country.unique()), 0)

# Selected type
grape_type = st.sidebar.selectbox("Selecione o tipo de uva", ['selecione'] + list(df_gsheet.grape_type.unique()), 0)

# Selected wine
wine_name = st.sidebar.selectbox("Selecione o nome do vinho", ['selecione'] + list(df_gsheet.wine_name.unique()), 0)

df_filtered = df_gsheet[(df_gsheet.price>=min_price) & (df_gsheet.price<=max_price)]
if country != 'selecione':
    df_filtered = df_filtered[df_filtered.country == country]
if wine_name != 'selecione':
    df_filtered = df_filtered[df_filtered.wine_name == wine_name]
if grape_type != 'selecione':
    df_filtered = df_filtered[df_filtered.grape_type == grape_type]

fig = go.Figure(data = go.Table(columnwidth=[], 
header=dict(values=["Vinho", "Tipo", "País", "Valor (R$)"], fill_color='#d73844', align='center'),
cells = dict(values=[df_filtered.wine_name, df_filtered.grape_type, df_filtered.country, df_filtered.price], align='left')
))

fig.update_layout(margin=dict(l=5, r=5, b=10, t=10),font=dict(size=18))

config = {'displayModeBar': False}
st.plotly_chart(fig, config=config)

# st.write(HTML(df_filtered['flag'].to_html(escape=False ,formatters=dict(flag=path_to_image_html))))
