import os
from fastapi import FastAPI, HTTPException
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from typing import List

app = FastAPI()

# Load the CSV file
ruta = 'Inv Marca Categoria.csv'
#encodings = ['utf-8', 'latin1', 'iso-8859-1', 'cp1252']

for encoding in encodings:
    try:
        #df = pd.read_csv(ruta, encoding=encoding, delimiter=';')
        df = pd.read_csv(ruta, delimiter=';')
        #print(f"correcto: {encoding}")
        break
    except (UnicodeDecodeError, pd.errors.ParserError) as e:
        print(f"fallido: {encoding} - {e}")
        df = pd.read_csv(ruta, delimiter=';')

# Data preprocessing
df.rename(columns={
    'Referencia': 'Codigo',
    'Cant. disponible': 'Existencia',
    'Notas ítem': 'Descripcion',
    'LINEA DE NEGOCIO': 'Linea',
    'CLASIFICACION': 'Clasificacion',
    'MARCA': 'Marca',
    'Costo prom. tot. (ins)': 'Costo'
}, inplace=True)
df['Marca'] = df['Marca'].str[7:].str.strip()

df['Existencia'] = pd.to_numeric(df['Existencia'], errors='coerce')
df['Costo'] = df['Costo'].replace({r'\$': '', r'\,': ''}, regex=True)
df['Costo'] = pd.to_numeric(df['Costo'], errors='coerce')
df['Costo'] = df['Costo'].apply(lambda x: x * 10)
for col in ['Codigo', 'Descripcion', 'Linea', 'Clasificacion', 'Marca']:
    df[col] = df[col].astype(str)

df = df.groupby('Codigo').sum()
df.drop(columns=['Bodega', 'Unnamed: 8'], inplace=True)
df['Codigo'] = df.index

# Define your response model here
class RecommendationResponse:
    # Define your fields here
    pass

@app.get("/especificar solicitud y marca", response_model=List[RecommendationResponse])
def recomendacion(prompt: str, marca: str):
    marca_upper = marca.upper()
    if marca_upper not in df['Marca'].values:
        raise HTTPException(status_code=404, detail="Marca no encontrada")
    
    df_temp = df[df['Marca'] == marca_upper].copy()
    df_temp['combined_text'] = df_temp['Descripcion'] + ' ' + df_temp['Linea'] + ' ' + df_temp['Clasificacion'] + ' ' + df_temp['Marca']
    df_temp['Existencia'] = pd.to_numeric(df_temp['Existencia'], errors='coerce')
    
    vectorizer = TfidfVectorizer(max_df=0.85, min_df=1, ngram_range=(2, 2), stop_words=['de', 'con', 'para', 'en', 'a'])
    X = vectorizer.fit_transform(df_temp['combined_text'].values.astype('U'))
    prompt_vectorized = vectorizer.transform([prompt])
    
    weights = [0.09]
    
    for w in weights:
        df_temp['Existencia_norm'] = df_temp['Existencia'] / df_temp['Existencia'].max()
        df_temp['weighted_score'] = cosine_similarity(X, prompt_vectorized).flatten() + (w * df_temp['Existencia_norm'])
        top_matches = df_temp.sort_values(by='weighted_score', ascending=False)
        top_matches = top_matches[top_matches['Existencia'] > 0].head(5)
        top_matches.reset_index(drop=True, inplace=True)

    return top_matches[['Codigo', 'Existencia', 'Costo']].to_dict(orient='records')
