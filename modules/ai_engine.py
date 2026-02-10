import openai
import streamlit as st
import json
import pandas as pd

def ejecutar_analisis_ia(sku, descripcion):
    sku_limpio = str(sku).replace("´", "").replace("'", "").strip()
    
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    
    # Prompt optimizado para términos clave como los que mencionas
    prompt = f"""
    Eres un experto en suministros industriales en Uruguay.
    Producto: {descripcion} (Código: {sku_limpio}).
    
    TAREA:
    Ignora el código si no lo encuentras. Busca productos equivalentes en Uruguay usando 
    palabras clave de la descripción (ej: Adhesivo, Cianocrilato, Limpiador, etc.).
    
    Identifica precios actuales en pesos uruguayos (UYU) o dólares (USD) en tiendas locales.
    Responde en JSON:
    {{
        "match_nombre": "Producto equivalente encontrado",
        "precio_competidor": 0.0,
        "moneda": "USD o UYU",
        "tienda": "Nombre del competidor uruguayo",
        "sugerencia": "Acción recomendada"
    }}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={ "type": "json_object" },
            temperature=0.3 # Mayor flexibilidad para encontrar coincidencias
        )
        data = json.loads(response.choices[0].message.content)
        data['sku_procesado'] = sku_limpio
        return data
    except:
        return None

def procesar_lote_industrial(df):
    resultados = []
    progreso = st.progress(0)
    
    # Detección de columnas (Material/Descripción)
    col_sku = 'Material' if 'Material' in df.columns else df.columns[0]
    col_desc = 'Descripción' if 'Descripción' in df.columns else df.columns[1]

    for index, row in df.iterrows():
        progreso.progress((index + 1) / len(df))
        
        # Procesar solo si hay descripción
        if pd.notna(row[col_desc]):
            datos = ejecutar_analisis_ia(row[col_sku], row[col_desc])
            # Solo añadir si se encontró un precio válido
            if datos and datos.get('precio_competidor', 0) > 0:
                resultados.append({
                    "SKU": datos['sku_procesado'],
                    "Producto Encontrado": datos['match_nombre'],
                    "Tienda": datos['tienda'],
                    "Precio": f"{datos['moneda']} {datos['precio_competidor']}",
                    "Sugerencia": datos['sugerencia']
                })
    return resultados
