import streamlit as st
import pandas as pd
import base64
import plotly.graph_objects as go

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
        padding-top: 25px !important;
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


@st.cache(allow_output_mutation=True)
def get_data(url):
    # Recupera dados da planilha do google sheets
    gsheet_url = url
    
    df_gsheet = pd.read_csv(gsheet_url, decimal=",")
    df_gsheet.rename(columns={"NOME":"wine_name", "TIPO":"grape_type", "ORIGEM":"country", "VALOR":"price", "UVA":"grape", "SUB_REGIAO":"region"}, inplace=True)
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

gsheets_url = st.secrets["gsheets_url"]
df_gsheet = get_data(gsheets_url)

# filters expander
my_expander = st.expander(label= 'Filtre por preço, produto, região e outros aqui!', expanded=True)
st.markdown(
            """
        <style>
        .streamlit-expanderHeader {
            font-size: 20px;
            text-align: center;
            font-weight: 500;
            padding: 20px 0px 0px 20px
        }
        </style>
        """,
        unsafe_allow_html=True)
df_expander = df_gsheet.copy()
with my_expander:
    st.markdown("---")
    
    # format price section
    price_settings = "<p style='font-size:18px; font-weight: 500'>Faixa de preço</p>"
    st.markdown(price_settings, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        min_price = st.number_input(label = 'A partir de R$',
                           min_value = df_gsheet.price.min(), 
                           max_value = df_gsheet.price.max(),
                           format = "%g",
                           value = 100.0,
                           step = 10.0)

    with col2:
        max_price = st.number_input(label = 'Até R$',
                           min_value = df_gsheet.price.min(), 
                           max_value = df_gsheet.price.max(),
                           value = 24000.0,
                           format = "%g",
                           step = 10.0)

    st.markdown("---")

    df_expander = df_expander[(df_expander.price>=min_price) & (df_expander.price<=max_price)]

    # Selected type
    grape_type = st.selectbox("Selecione o tipo de produto", ['selecione'] + list(df_expander.grape_type.unique()), 0)
    if grape_type != 'selecione':
        df_expander = df_expander[df_expander.grape_type == grape_type]

    # Selected grape
    grape = st.selectbox("Selecione a uva (se for vinho)", ['selecione'] + list(df_expander.grape.str.split("/").explode().str.strip().unique()), 0)
    if grape != 'selecione':
        df_expander = df_expander[df_expander.grape.str.contains(grape)]

    # Selected country
    country = st.selectbox("Selecione o país", ['selecione'] + list(df_expander.country.unique()), 0)
    if country != 'selecione':
        df_expander = df_expander[df_expander.country == country]

    # Selected region
    region = st.selectbox("Selecione a região/sub-região", ['selecione'] + list(df_expander.region.str.split("/").explode().str.strip().unique()), 0)
    if region != 'selecione':
        df_expander = df_expander[df_expander.region.str.contains(region)]

    # Selected wine
    wine_name = st.selectbox("Selecione o nome do produto", ['selecione'] + list(df_expander.wine_name.unique()), 0)
    if wine_name != 'selecione':
        df_expander = df_expander[df_expander.wine_name == wine_name]

    # Filter button
    m = st.markdown("""
    <style>
    div.stButton > button:first-child {
        color: #ffffff; 
        background-color:#D73844;
        margin:0 auto;
        display:block;
    }
    </style>""", unsafe_allow_html=True)
    filter_apply = st.button('Filtrar produtos!')
    sem_filtro = "<p style='text-align: center; font-size: 12px'>Para acessar o Catalogo completo, clique em Filtrar produtos sem selecionar nenhum filtro!</p>"
    st.markdown(sem_filtro, unsafe_allow_html=True)

if filter_apply:

    df_filtered = df_gsheet[(df_gsheet.price>=min_price) & (df_gsheet.price<=max_price)]
    if country != 'selecione':
        df_filtered = df_filtered[df_filtered.country == country]
    if wine_name != 'selecione':
        df_filtered = df_filtered[df_filtered.wine_name == wine_name]
    if grape_type != 'selecione':
        df_filtered = df_filtered[df_filtered.grape_type == grape_type]
    if grape != 'selecione':
        df_filtered = df_filtered[df_filtered.grape.str.contains(grape)]
    if region != 'selecione':
        df_filtered = df_filtered[df_filtered.region.str.contains(region)]

    df_filtered['price'] = df_filtered['price'].apply(lambda x: "R${:.2f}".format(x))
    df_filtered.rename(columns={"wine_name": "Nome", "grape_type": "Tipo", "country": "Pais", "price": "Valor", "grape": "Uva", "region": "Regiao"}, inplace=True)
    df_filtered = df_filtered[["Nome", "Tipo", "Uva", "Pais", "Regiao", "Valor"]]
    
    df_filtered.reset_index(drop=True, inplace=True)
    s = df_filtered.style.set_properties(**{'background-color': '#F0F2F6',              
                                                 'border-color': 'black',
                                                 'overflow-x': 'scroll'})
    
    st.markdown('<style>.ReactVirtualized__Grid__innerScrollContainer div[class^="col_heading"]{ background:#d73844; font-size: 18px; color:black} </style>', unsafe_allow_html=True)
    st.dataframe(s, height=900)
