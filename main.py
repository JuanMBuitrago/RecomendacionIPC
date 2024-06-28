# -*- coding: utf-8 -*-
"""RecomendacionIPC.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1fJpb2XgdGkcmwQmRlOBKycik8_E4VmKu
"""

import os
from fastapi import FastAPI
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import pandas as pd
ruta = 'Inv Marca Categoria.csv'
encodings = ['utf-8', 'latin1', 'iso-8859-1', 'cp1252']

#for encoding in encodings:
#    try:
        #df = pd.read_csv(ruta, encoding=encoding, delimiter=';')
        #print(f"correcto: {encoding}")
#        break
#    except (UnicodeDecodeError, pd.errors.ParserError) as e:
#        print(f"fallido: {encoding} - {e}")
df = pd.read_csv(ruta)
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

app = FastAPI()

@app.get("/especificar solicitud y marca", response_model=List[RecommendationResponse])
def recomendacion(prompt: str, marca: str):
  marca_upper = marca.upper()
  if marca_upper in df['Marca'].values:
    df_temp = df[df['Marca'] == marca.upper()].copy()
  else:
    return print('Marca no encontrada')
  df_temp['combined_text'] = df['Descripcion'] + ' ' + df['Linea'] + ' ' + df['Clasificacion'] + ' ' + df['Marca']
  app = FastAPI()

  df_temp['Existencia'] = pd.to_numeric(df_temp['Existencia'],errors='coerce')
  vectorizer = TfidfVectorizer(max_df=0.85, min_df=1, ngram_range=(2, 2), stop_words=['de', 'con','para','en', 'a'])
  X = vectorizer.fit_transform(df_temp['combined_text'].values.astype('U'))
  prompt_vectorized = vectorizer.transform([prompt])

  weights = [0.09]

  for w in weights:
      df_temp['Existencia_norm'] = df_temp['Existencia'] / df_temp['Existencia'].max()
      df_temp['weighted_score'] = cosine_similarity(X, prompt_vectorized).flatten() + (w * df_temp['Existencia_norm'])
      df_temp['weighted_score'] = cosine_similarity(X, prompt_vectorized).flatten()
      top_matches = df_temp.sort_values(by='weighted_score', ascending=False)
      top_matches = top_matches[top_matches['Existencia'] > 0].head(5)
      top_matches.reset_index(drop=True, inplace=True)

      #print(f"Productos sugueridos (w = {w}):")
  print(top_matches[['Codigo', 'Existencia', 'Costo']])
  return top_matches[['Codigo', 'Existencia', 'Costo']]


'''Used to found commom stopwords, disregard unless used for new database'''
#from collections import Counter
#import re
#all_notes = ' '.join(df['Descripcion'])
#words = re.findall(r'\b\w+\b', all_notes.lower())
#word_counts = Counter(words)
#most_common_words = word_counts.most_common()
#for word, count in most_common_words:
#    print(f"{word}: {count}")
