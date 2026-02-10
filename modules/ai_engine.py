import openai
import streamlit as st
import json
import pandas as pd

def ejecutar_analisis_ia(sku, descripcion):
    sku_limpio = str(sku).replace("´", "").replace("'", "").strip()
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    
    prompt = f"""
    Eres experto en mercado industrial uruguayo. Producto: {descripcion} (Código: {sku_limpio}).
    TAREA: Busca equivalentes comerciales en Uruguay (Mercado Libre UY, ferreterías locales).
    Responde en JSON:
    {{
        "match_nombre": "Producto encontrado",
        "precio_competidor": 0.0,
        "moneda": "USD/UYU",
        "tienda": "Tienda en Uruguay",
        "sugerencia": "Acción"
    }}
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={ "type": "json_object" }
        )
        data = json.loads(response.choices[0].message.content)
        data['sku_procesado'] = sku_limpio
        return data
    except:
        return None

def procesar_lote_industrial(df):
    resultados = []
    progreso = st.progress(0)
    col_sku = 'Material' if 'Material' in df.columns else df.columns[0]
    col_desc = 'Descripción' if 'Descripción' in df.columns else df.columns[1]

    for index, row in df.iterrows():
        progreso.progress((index + 1) / len(df))
        if pd.notna(row[col_desc]):
            datos = ejecutar_analisis_ia(row[col_sku], row[col_desc])
            if datos and datos.get('precio_competidor', 0) > 0:
                resultados.append({
                    "SKU": datos['sku_procesado'],
                    "Equivalente": datos['match_nombre'],
                    "Tienda": datos['tienda'],
                    "Precio": f"{datos['moneda']} {datos['precio_competidor']}",
                    "Sugerencia": datos['sugerencia']
                })
    return resultados
