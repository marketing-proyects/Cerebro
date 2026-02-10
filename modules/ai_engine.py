import openai
import streamlit as st
import json
import pandas as pd

def limpiar_y_optimizar_descripcion(texto):
    if pd.isna(texto): return "Producto industrial"
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": f"Optimiza para búsqueda: {texto}"}],
            temperature=0
        )
        return response.choices[0].message.content
    except:
        return str(texto).replace("-", " ")

def ejecutar_analisis_ia(sku, descripcion):
    # LIMPIEZA: Eliminamos el carácter ´ o ' que protege el cero
    sku_limpio = str(sku).replace("´", "").replace("'", "").strip()
    desc_optima = limpiar_y_optimizar_descripcion(descripcion)
    
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    prompt = f"Producto: {desc_optima} (SKU: {sku_limpio}). Investiga competidores en Uruguay. Responde JSON: match_nombre, precio_competidor, moneda, tienda, sugerencia."
    
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
    
    # Identificar columnas
    col_sku = 'Material' if 'Material' in df.columns else df.columns[0]
    col_desc = 'Descripción' if 'Descripción' in df.columns else df.columns[1]

    for index, row in df.iterrows():
        progreso.progress((index + 1) / len(df))
        datos = ejecutar_analisis_ia(row[col_sku], row[col_desc])
        if datos:
            resultados.append({
                "SKU": datos['sku_procesado'],
                "Mercado": datos['match_nombre'],
                "Competidor": datos['tienda'],
                "Precio": f"{datos['moneda']} {datos['precio_competidor']}",
                "Sugerencia": datos['sugerencia']
            })
    return resultados
