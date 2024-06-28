from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = FastAPI()

class RecommendationResponse(BaseModel):
    Codigo: str
    Existencia: int
    Costo: float

@app.get("/recomendacion", response_model=List[RecommendationResponse])
def recomendacion(prompt: str, marca: str):
    try:
        df = pd.read_csv('Inv Marca Categoria.csv')
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="CSV file not found")

    marca_upper = marca.upper()
    if marca_upper not in df['Marca'].values:
        raise HTTPException(status_code=404, detail="Marca not found")
    
    df_temp = df[df['Marca'] == marca_upper].copy()
    df_temp['combined_text'] = df_temp['Descripcion'] + ' ' + df_temp['Linea'] + ' ' + df_temp['Clasificacion'] + ' ' + df_temp['Marca']

    df_temp['Existencia'] = pd.to_numeric(df_temp['Existencia'], errors='coerce')
    vectorizer = TfidfVectorizer(max_df=0.85, min_df=1, ngram_range=(2, 2), stop_words=['de', 'con','para','en', 'a'])
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
