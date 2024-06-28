import pandas as pd

ruta = 'Inv Marca Categoria.csv'
encodings = ['utf-8', 'latin1', 'iso-8859-1', 'cp1252']

for encoding in encodings:
    try:
        df = pd.read_csv(ruta, encoding=encoding, delimiter=';')
        print(f"correcto: {encoding}")
        break
    except (UnicodeDecodeError, pd.errors.ParserError) as e:
        print(f"fallido: {encoding} - {e}")
df.rename(columns=({'Referencia': 'Codigo', 'Cant. disponible': 'Existencia', 'Notas ítem': 'Descripcion', 'LINEA DE NEGOCIO': 'Linea',
                    'CLASIFICACION': 'Clasificacion', 'MARCA': 'Marca', 'Costo prom. tot. (ins)': 'Costo'}),inplace=True)
df['Marca'] = df['Marca'].str[7:].str.strip()

#print(df.head())
#df['Marca'].unique()

df['Existencia'] = pd.to_numeric(df['Existencia'],errors='coerce')
remplazo = {r'\$': '', r'\,': ''}
df['Costo'] = df['Costo'].replace(remplazo, regex=True)
df['Costo'] = pd.to_numeric(df['Costo'],errors='coerce')
df['Costo'] = df['Costo'].apply(lambda x: x*10)
for col in ['Codigo', 'Descripcion', 'Linea', 'Clasificacion', 'Marca']:
  df[col] = df[col].astype(str)
#df.head()

df = df.groupby('Codigo').sum()
df.drop(columns= ['Bodega', 'Unnamed: 8'], inplace=True)

df['Codigo'] = df.index
