from google import genai
from google.genai import types
import openai
import streamlit as st
import json
import pandas as pd
import re
import time

def ejecutar_analisis_ia(descripcion, url_ref=None):
    # Limpieza: Borramos códigos de Würth
    desc_limpia = re.sub(r'\d{5,}', '', str(descripcion)).strip()
    
    prompt = f"""
    ERES UN INVESTIGADOR DE MERCADO INDUSTRIAL EN URUGUAY.
    PRODUCTO: "{desc_limpia}"
    REF TÉCNICA: {url_ref}

    METODOLOGÍA:
    1. Identifica qué es el producto técnicamente.
    2. BUSCA EN URUGUAY: Mercado Libre UY, Sodimac, Ingco, Salvador Livio o Pampín.
    3. COMPETENCIA: Busca marcas como Sika, Fischer, 3M, Stanley o Bosch.
    
    Responde estrictamente en JSON:
    {{
        "comp": "Marca y modelo competidor",
        "tienda": "Tienda en Uruguay",
        "imp": "Marca/Importador",
        "precio": 0.0,
        "moneda": "USD/UYU",
        "um": "Presentación",
        "link": "URL del hallazgo en Uruguay",
        "vs": "Análisis de reemplazo"
    }}
    """

    if "GOOGLE_API_KEY" in st.secrets:
        # Intentamos hasta 2 veces si hay error de cuota
        for intento in range(2):
            try:
                client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
                google_search_tool = types.Tool(google_search=types.GoogleSearch())
                
                # Usamos 1.5 Flash que es más estable para cuotas gratuitas
                response = client.models.generate_content(
                    model="gemini-1.5-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(tools=[google_search_tool])
                )
                
                res_text = response.text
                if "```json" in res_text:
                    res_text = res_text.split("```json")[1].split("```")[0].strip()
                return json.loads(res_text)
            
            except Exception as e:
                if "429" in str(e):
                    time.sleep(10) # Esperamos 10 segundos si la cuota se agota
                    continue
                st.error(f"Error técnico: {e}")
                break

    return {
        "comp": "Cuota excedida", "tienda": "Reintentar en 1 min", "imp": "N/A", 
        "precio": 0, "moneda": "N/A", "um": "N/A", "link": "N/A", "vs": "Google API Limit"
    }

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
            status_text.text(f"🕵️ Investigando {index + 1} de {total}: {desc_actual[:30]}...")
            
            url_val = row[col_url] if col_url and pd.notna(row[col_url]) else None
            datos = ejecutar_analisis_ia(desc_actual, url_val)
            
            resultados.append({
                "Descripción Original": desc_actual,
                "Producto Competidor": datos.get('comp'),
                "Tienda": datos.get('tienda'),
                "Precio": datos.get('precio'),
                "Moneda": datos.get('moneda'),
                "Link Hallazgo": datos.get('link'),
                "Análisis": datos.get('vs')
            })
            # PAUSA DE SEGURIDAD: Evita el error 429
            time.sleep(4) 
    
    status_text.empty()
    progreso.empty()
    return resultados
