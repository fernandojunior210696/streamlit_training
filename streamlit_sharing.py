# Título do dashboard
st.title("Catálogo de vinhos Woods Wine")

# Recupera dados da planilha do google sheets
gsheet_url = st.secrets["public_gsheets_url"]
# gsheet_url = st.secrets["public_gsheets_url"]
conn = connect()
rows = conn.execute(f'SELECT NOME AS wine_name, TIPO AS grape_type, ORIGEM AS country, VALOR AS price  FROM "{gsheet_url}"')

# Converte dados para pandas df
df_gsheet = pd.DataFrame(rows)

# values = st.sidebar.slider("Preço dos vinhos", float(df_gsheet.VALOR.min()), 1000., (50., 3000.))
st.sidebar.markdown("# Filtros disponíveis")
values = st.sidebar.slider(label = "Preço dos vinhos", 
                           min_value = df_gsheet.price.min(), 
                           max_value = df_gsheet.price.max(),
                           value = (df_gsheet.price.min(), df_gsheet.price.max()))

# Selected price range
min_price=values[0]
max_price=values[1]

# Selected country
country = st.sidebar.selectbox("Selecione o país", ['selecione'] + list(df_gsheet.country.unique()), 0)

# Selected wine
wine_name = st.sidebar.selectbox("Selecione o nome do vinho", ['selecione'] + list(df_gsheet.wine_name.unique()), 0)

# Selected wine
grape_type = st.sidebar.selectbox("Selecione o tipo de uva", ['selecione'] + list(df_gsheet.grape_type.unique()), 0)

df_filtered = df_gsheet[(df_gsheet.price>=min_price) & (df_gsheet.price<=max_price)]
if country != 'selecione':
    df_filtered = df_filtered[df_filtered.country == country]
if wine_name != 'selecione':
    df_filtered = df_filtered[df_filtered.wine_name == wine_name]
if grape_type != 'selecione':
    df_filtered = df_filtered[df_filtered.grape_type == grape_type]

st.write(df_filtered)
