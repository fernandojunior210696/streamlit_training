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


@st.cache(allow_output_mutation=False)
def get_data(url):
    # Recupera dados da planilha do google sheets

#     sheet_id = st.secrets["sheet_id"]
#     sheet_name = st.secrets["sheet_name"]
    gsheet_url = url
#     url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    
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
my_expander = st.expander(label= 'Filtre por produto, preço, região e outros aqui!', expanded=True)
with my_expander:
    values = st.slider(label = "Preço dos produtos", 
                           min_value = df_gsheet.price.min(), 
                           max_value = df_gsheet.price.max(),
                           value = (float(df_gsheet.price.min()), float(df_gsheet.price.max())),
                           format = "R$%g")

    # Selected price range
    min_price=values[0]
    max_price=values[1]

    # Selected type
    grape_type = st.selectbox("Selecione o tipo de produto", ['selecione'] + list(df_gsheet.grape_type.unique()), 0)
    
    # Selected grape
    grape = st.selectbox("Selecione a uva (se for vinho)", ['selecione'] + list(df_gsheet.grape.str.split("/").explode().str.strip().unique()), 0)

    # Selected country
    country = st.selectbox("Selecione o país", ['selecione'] + list(df_gsheet.country.unique()), 0)

    # Selected region
    region = st.selectbox("Selecione a região/sub-região", ['selecione'] + list(df_gsheet.region.str.split("/").explode().str.strip().unique()), 0)

    # Selected wine
    wine_name = st.selectbox("Selecione o nome do produto", ['selecione'] + list(df_gsheet.wine_name.unique()), 0)

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
#     st.markdown('<style>.ReactVirtualized__Grid__innerScrollContainer div[class^="row"]{ background:#d73844; display: none; } </style>', unsafe_allow_html=True)
    st.dataframe(s, height=900)
