import openai
import streamlit as st
import json
import pandas as pd

def ejecutar_analisis_ia(sku, descripcion):
    # Limpieza de caracteres del SKU
    sku_limpio = str(sku).replace("´", "").replace("'", "").strip()
    
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    
    # Prompt mejorado para búsqueda semántica (No solo SKU)
    prompt = f"""
    Eres un analista de mercado en Uruguay. 
    Producto a investigar: {descripcion} (Código interno: {sku_limpio}).
    
    INSTRUCCIONES:
    1. Si no encuentras el código exacto, busca por los términos de la descripción (ej: 'Limpiador de Frenos', 'Silicona Neutra').
    2. Identifica competidores locales (Mercado Libre Uruguay, Tienda Inglesa, Sodimac, Ferreterías industriales).
    3. Responde estrictamente en JSON con este formato:
    {{
        "match_nombre": "Nombre del producto equivalente encontrado",
        "precio_competidor": 0.0,
        "moneda": "USD o UYU",
        "tienda": "Nombre del comercio uruguayo",
        "sugerencia": "Breve recomendación comercial"
    }}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={ "type": "json_object" },
            temperature=0.2 # Un poco de creatividad para encontrar equivalentes
        )
        data = json.loads(response.choices[0].message.content)
        data['sku_procesado'] = sku_limpio
        return data
    except:
        return None

def procesar_lote_industrial(df):
    resultados = []
    progreso = st.progress(0)
    
    # Identificar columnas Material/Descripción
    col_sku = 'Material' if 'Material' in df.columns else df.columns[0]
    col_desc = 'Descripción' if 'Descripción' in df.columns else df.columns[1]

    for index, row in df.iterrows():
        progreso.progress((index + 1) / len(df))
        
        # Ignorar filas donde la descripción esté vacía
        if pd.isna(row[col_desc]): continue
        
        datos = ejecutar_analisis_ia(row[col_sku], row[col_desc])
        if datos and datos.get('precio_competidor', 0) > 0:
            resultados.append({
                "SKU Original": datos['sku_procesado'],
                "Producto Encontrado": datos['match_nombre'],
                "Competidor": datos['tienda'],
                "Precio Mercado": f"{datos['moneda']} {datos['precio_competidor']}",
                "Acción Sugerida": datos['sugerencia']
            })
    return resultados
