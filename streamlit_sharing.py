from email import header
import streamlit as st
import pandas as pd
from gsheetsdb import connect
from IPython.core.display import HTML

import plotly.express as px
import plotly.graph_objects as go

logo, title = st.columns(2)

# page title
st.set_page_config(page_title="Catálogo de Produtos - Woods Wine", layout="centered")

LOGO_IMAGE = "./images/logo.jpg"

st.markdown(
    """
    <style>
    .container {
        display: flex;
    }
    .logo-text {
        font-weight:700 !important;
        font-size:50px !important;
        color: #f9a01b !important;
        padding-top: 75px !important;
    }
    .logo-img {
        display: block;
        margin-left: auto;
        margin-right: auto;
        width: 50%;
    }
    </style>
    """,
    unsafe_allow_html=True
)


st.markdown(
    f"""
    <div class="container">
        <img class="logo-img" src="data:image/png;base64,{base64.b64encode(open(LOGO_IMAGE, "rb").read()).decode()}">
    </div>
    """,
    unsafe_allow_html=True
)


# hide streamlit menu
st.markdown(""" <style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style> """, unsafe_allow_html=True)

title_settings = "<h1 style='text-align: center; color: #D73844; background-color:#46172D;'>Catálogo de Produtos</h1>"
st.markdown(title_settings, unsafe_allow_html=True)


@st.cache
def get_data(url):
    # Recupera dados da planilha do google sheets
    gsheet_url = url
    # gsheet_url = st.secrets["public_gsheets_url"]
    conn = connect()
    rows = conn.execute('SELECT NOME AS wine_name, TIPO AS grape_type, ORIGEM AS country, VALOR AS price, UVA AS grape, SUB_REGIAO AS region FROM "{a}"'.format(a=gsheet_url))

    # Converte dados para pandas df
    df_gsheet = pd.DataFrame(rows)
    df_gsheet.fillna("-", inplace= True)
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

# filters expander
my_expander = st.expander(label= 'Filtre aqui os produtos desejados!')
with my_expander:

    values = st.slider(label = "Preço dos produtos", 
                           min_value = df_gsheet.price.min(), 
                           max_value = df_gsheet.price.max(),
                           value = (float(df_gsheet.price.min()), float(df_gsheet.price.max())),
                           format = "R$%g")

    # Selected price range
    min_price=values[0]
    max_price=values[1]

    # Selected country
    country = st.selectbox("Selecione o país", ['selecione'] + list(df_gsheet.country.unique()), 0)

    # Selected region
    region = st.selectbox("Selecione a região/sub-regiao", ['selecione'] + list(df_gsheet.region.unique()), 0)

    # Selected type
    grape_type = st.selectbox("Selecione o tipo de produto", ['selecione'] + list(df_gsheet.grape_type.unique()), 0)

    # Selected wine
    wine_name = st.selectbox("Selecione o nome do vinho", ['selecione'] + list(df_gsheet.wine_name.unique()), 0)

    # Selected grape
    grape = st.selectbox("Selecione a uva", ['selecione'] + list(df_gsheet.grape.str.split("/").explode().unique()), 0)

df_filtered = df_gsheet[(df_gsheet.price>=min_price) & (df_gsheet.price<=max_price)]
if country != 'selecione':
    df_filtered = df_filtered[df_filtered.country == country]
if wine_name != 'selecione':
    df_filtered = df_filtered[df_filtered.wine_name == wine_name]
if grape_type != 'selecione':
    df_filtered = df_filtered[df_filtered.grape_type == grape_type]
if grape != 'selecione':
    # df_filtered = df_filtered[df_filtered.grape == grape]
    df_filtered = df_filtered[df_filtered.grape.str.contains(grape)]
if region != 'selecione':
    df_filtered = df_filtered[df_filtered.region == region]

df_filtered['price'] = df_filtered['price'].apply(lambda x: "R${:.2f}".format(x))
df_filtered.rename(columns={"wine_name": "Nome", "grape_type": "Tipo", "country": "País", "price": "Valor", "grape": "Uva", "region": "Sub Região"}, inplace=True)

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
