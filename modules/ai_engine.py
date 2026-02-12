import openai
import streamlit as st
import json
import pandas as pd

def ejecutar_analisis_ia(sku, descripcion, url_ref=None):
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    
    prompt = f"""
    Eres un experto en Business Intelligence industrial en Uruguay.
    Producto Würth de referencia: {descripcion} (SKU: {sku})
    URL Técnica: {url_ref}

    TAREA:
    1. Si la URL es de otro país, analiza las propiedades técnicas del producto.
    2. Busca en Uruguay (Mercado Libre, Sodimac, Ferreterías Industriales) el equivalente comercial.
    3. Separa TIENDA de IMPORTADOR/MARCA.
    
    Responde en JSON con este formato exacto:
    {{
        "comp": "Nombre producto competencia",
        "tienda": "Tienda en Uruguay",
        "imp": "Importador o Marca",
        "precio": 0.0,
        "moneda": "USD/UYU",
        "um": "Presentación (ej: 310ml)",
        "link": "Link competencia",
        "rank": "Puntaje/Opiniones",
        "vs": "Würth vs Comp",
        "obs": "Promociones o notas"
    }}
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={ "type": "json_object" }
        )
        data = json.loads(response.choices[0].message.content)
        data['sku'] = sku
        data['desc'] = descripcion
        return data
    except:
        return None

def procesar_lote_industrial(df):
    resultados = []
    progreso = st.progress(0)
    
    col_sku = 'Material' if 'Material' in df.columns else df.columns[0]
    col_desc = 'Descripción' if 'Descripción' in df.columns else df.columns[1]
    col_url = 'URL' if 'URL' in df.columns else (df.columns[2] if len(df.columns) > 2 else None)

    for index, row in df.iterrows():
        progreso.progress((index + 1) / len(df))
        if pd.notna(row[col_desc]):
            url = row[col_url] if col_url else None
            datos = ejecutar_analisis_ia(row[col_sku], row[col_desc], url)
            if datos:
                resultados.append({
                    "SKU Würth": datos['sku'],
                    "Producto Competidor": datos['comp'],
                    "Tienda (Venta)": datos['tienda'],
                    "Importador/Marca": datos['imp'],
                    "Precio": datos['precio'],
                    "Moneda": datos['moneda'],
                    "Presentación": datos['um'],
                    "Link": datos['link'],
                    "Würth vs Comp.": datos['vs'],
                    "Observaciones": datos['obs']
                })
    return resultados
