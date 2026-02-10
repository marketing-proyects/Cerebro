import openai
import streamlit as st
import json
import pandas as pd

def ejecutar_analisis_ia(sku, descripcion):
    # Limpiamos el SKU de tildes o comas
    sku_limpio = str(sku).replace("´", "").replace("'", "").strip()
    
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    
    # Prompt enfocado en búsqueda semántica descriptiva
    prompt = f"""
    Eres un experto en el mercado industrial de Uruguay.
    Producto: {descripcion} (Código: {sku_limpio}).
    
    Busca productos equivalentes en Uruguay usando los términos clave de la descripción.
    Ignora el código si no lo encuentras en bases de datos públicas.
    Responde estrictamente en JSON:
    {{
        "match_nombre": "Producto equivalente encontrado",
        "precio_competidor": 0.0,
        "moneda": "USD o UYU",
        "tienda": "Competidor uruguayo",
        "sugerencia": "Recomendación"
    }}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={ "type": "json_object" },
            temperature=0.3
        )
        data = json.loads(response.choices[0].message.content)
        data['sku_procesado'] = sku_limpio
        return data
    except:
        return None

def procesar_lote_industrial(df):
    resultados = []
    progreso = st.progress(0)
    
    # Aseguramos detección de columnas
    col_sku = 'Material' if 'Material' in df.columns else df.columns[0]
    col_desc = 'Descripción' if 'Descripción' in df.columns else df.columns[1]

    for index, row in df.iterrows():
        progreso.progress((index + 1) / len(df))
        
        if pd.notna(row[col_desc]):
            datos = ejecutar_analisis_ia(row[col_sku], row[col_desc])
            # Si el precio es 0, la IA no encontró nada útil, no lo agregamos
            if datos and datos.get('precio_competidor', 0) > 0:
                resultados.append({
                    "SKU": datos['sku_procesado'],
                    "Equivalente": datos['match_nombre'],
                    "Competidor": datos['tienda'],
                    "Precio": f"{datos['moneda']} {datos['precio_competidor']}",
                    "Sugerencia": datos['sugerencia']
                })
    return resultados
