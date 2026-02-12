import google.generativeai as genai
import openai
import streamlit as st
import json
import pandas as pd
import re
import time

def ejecutar_analisis_ia(descripcion, url_ref=None):
    # Limpiamos los códigos de Würth para que no ensucien la búsqueda
    desc_limpia = re.sub(r'\d{5,}', '', str(descripcion)).strip()
    
    prompt = f"""
    Eres un experto en compras industriales en Uruguay. 
    Tu objetivo es encontrar el precio de un COMPETIDOR para: "{desc_limpia}"
    Usa esta referencia técnica para entender el producto: {url_ref}

    INSTRUCCIONES DE BÚSQUEDA DIRIGIDA:
    1. Busca el producto exclusivamente en dominios de URUGUAY (.com.uy).
    2. Prioriza resultados de estos sitios específicos:
       - mercadolibre.com.uy
       - sodimac.com.uy
       - ingco.com.uy
       - salvadorlivio.com.uy
       - pampin.com.uy
    3. Busca marcas competidoras líderes: Sika, Fischer, 3M, Stanley, Bosch o Ingco.
    4. Provee el precio actual y el link directo del hallazgo.

    Responde ESTRICTAMENTE en este formato JSON:
    {{
        "comp": "Marca y modelo competidor",
        "tienda": "Nombre del comercio en Uruguay",
        "precio": 0.0,
        "moneda": "USD/UYU",
        "um": "Presentación (ej. 310ml)",
        "link": "URL exacta del producto en Uruguay",
        "vs": "Comparativa técnica rápida"
    }}
    """

    # --- VOLVEMOS AL MOTOR ESTABLE (genai original) ---
    if "GOOGLE_API_KEY" in st.secrets:
        try:
            genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
            # Usamos 1.5-flash que es el más estable y rara vez da error de cuota
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            
            res_text = response.text.replace('```json', '').replace('```', '').strip()
            return json.loads(res_text)
        except Exception as e:
            # Si hay un error, devolvemos una estructura vacía pero segura
            return None

    return None

def procesar_lote_industrial(df):
    resultados = []
    status_text = st.empty()
    progreso = st.progress(0)
    
    col_desc = next((c for c in ['DESCRIPCION CORTA', 'Descripción'] if c in df.columns), df.columns[0])
    col_url = next((c for c in ['URL (Opcional pero recomendada)', 'URL', 'Link'] if c in df.columns), None)

    total = len(df)
    for index, row in df.iterrows():
        pct = (index + 1) / total
        progreso.progress(pct)
        
        desc_actual = str(row[col_desc])
        if pd.notna(row[col_desc]) and desc_actual.lower() != 'none':
            status_text.text(f"🔎 Investigando {index + 1} de {total}: {desc_actual[:30]}...")
            
            url_val = row[col_url] if col_url and pd.notna(row[col_url]) else None
            
            # Llamada a la IA
            datos = ejecutar_analisis_ia(desc_actual, url_val)
            
            if datos:
                resultados.append({
                    "Descripción Original": desc_actual,
                    "Competidor": datos.get('comp'),
                    "Tienda": datos.get('tienda'),
                    "Precio": datos.get('precio'),
                    "Moneda": datos.get('moneda'),
                    "Link Hallazgo": datos.get('link'),
                    "Análisis": datos.get('vs')
                })
            
            # Un pequeño respiro de 2 segundos para evitar cualquier bloqueo de la API
            time.sleep(2)
            
    status_text.empty()
    progreso.empty()
    return resultados
