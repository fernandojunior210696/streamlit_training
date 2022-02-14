from email import header
import streamlit as st
import pandas as pd
from gsheetsdb import connect
from IPython.core.display import HTML

import plotly.express as px
import plotly.graph_objects as go

logo, title = st.columns(2)

with logo:
    st.image('./images/logo_woods.png',use_column_width='auto')

with title:
    st.markdown("<h2 style='text-align: right; line-height: 100px; '>Catálogo Woods Wine</h2>", unsafe_allow_html=True)

st.markdown("---")
st.markdown("<p style='text-align: center; font-size: 32px; '>Filtre abaixo por país, tipo de uva, faixa de preço ou pelo nome do vinho e faça sua escolha!</p>", unsafe_allow_html=True)

@st.cache
def get_data(url):
    # Recupera dados da planilha do google sheets
    gsheet_url = url
    # gsheet_url = st.secrets["public_gsheets_url"]
    conn = connect()
    rows = conn.execute(f'SELECT NOME AS wine_name, TIPO AS grape_type, ORIGEM AS country, VALOR AS price FROM "{gsheet_url}"')

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

values = st.slider(label = "Preço dos vinhos", 
                           min_value = df_gsheet.price.min(), 
                           max_value = df_gsheet.price.max(),
                           value = (float(df_gsheet.price.min()), float(df_gsheet.price.max())),
                           format = "R$%g")

# Selected price range
min_price=values[0]
max_price=values[1]

# Selected country
country = st.selectbox("Selecione o país", ['selecione'] + list(df_gsheet.country.unique()), 0)

# Selected type
grape_type = st.selectbox("Selecione o tipo de uva", ['selecione'] + list(df_gsheet.grape_type.unique()), 0)

# Selected wine
wine_name = st.selectbox("Selecione o nome do vinho", ['selecione'] + list(df_gsheet.wine_name.unique()), 0)

df_filtered = df_gsheet[(df_gsheet.price>=min_price) & (df_gsheet.price<=max_price)]
if country != 'selecione':
    df_filtered = df_filtered[df_filtered.country == country]
if wine_name != 'selecione':
    df_filtered = df_filtered[df_filtered.wine_name == wine_name]
if grape_type != 'selecione':
    df_filtered = df_filtered[df_filtered.grape_type == grape_type]

df_filtered['price'] = df_filtered['price'].apply(lambda x: "R${:.2f}".format(x))
df_filtered.rename(columns={"wine_name": "Nome", "grape_type": "Tipo", "country": "País", "price": "Valor"}, inplace=True)

# CSS to inject contained in a string
hide_table_row_index = """
            <style>
            tbody th {display:none}
            .blank {display:none}
            </style>
            """

# Inject CSS with Markdown
st.markdown(hide_table_row_index, unsafe_allow_html=True)

# Display a static table

headers = {
    'selector': 'th:not(.index_name)',
    'props': [('background-color', '#d73844'), ('color', 'white')]
}

rows = {
    'selector': 'td',
    'props': [('background-color', '#F0F2F6'), ('color', '#000000')]
}

st.table(df_filtered.style.hide_index().set_table_styles([headers, rows]))