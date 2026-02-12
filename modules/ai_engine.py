from google import genai
from google.genai import types
import openai
import streamlit as st
import json
import pandas as pd
import re

def ejecutar_analisis_ia(descripcion, url_ref=None):
    # Limpieza: Borramos códigos de Würth para que la IA busque el producto, no el SKU
    desc_limpia = re.sub(r'\d{5,}', '', str(descripcion)).strip()
    
    prompt = f"""
    ERES UN INVESTIGADOR DE MERCADO INDUSTRIAL EN URUGUAY.
    
    PRODUCTO A ANALIZAR: "{desc_limpia}"
    REFERENCIA TÉCNICA: {url_ref}

    INSTRUCCIONES DE BÚSQUEDA:
    1. Usa la descripción y la URL para entender la función técnica (ej. Adhesivo MS, Disco de corte).
    2. BUSCA EN URUGUAY: Usa Google Uruguay para encontrar precios en Mercado Libre UY, Sodimac, Ingco, Salvador Livio o Pampín.
    3. COMPETENCIA: Busca marcas como Sika, Fischer, 3M, Stanley o Bosch disponibles en Uruguay.
    4. RESPUESTA: Provee precio real, tienda y link. No acepto campos vacíos.

    Responde ESTRICTAMENTE en JSON:
    {{
        "comp": "Marca y modelo competidor",
        "tienda": "Tienda en Uruguay",
        "imp": "Marca/Importador",
        "precio": 0.0,
        "moneda": "USD/UYU",
        "um": "Presentación",
        "link": "URL del hallazgo en Uruguay",
        "vs": "Breve análisis de reemplazo"
    }}
    """

    # --- MOTOR GOOGLE GENAI (MODERNO) ---
    if "GOOGLE_API_KEY" in st.secrets:
        try:
            client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
            
            # Activamos la herramienta de búsqueda de Google (Google Search Grounding)
            google_search_tool = types.Tool(google_search=types.GoogleSearch())
            
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
                config=types.GenerateContentConfig(tools=[google_search_tool])
            )
            
            res_text = response.text
            if "```json" in res_text:
                res_text = res_text.split("```json")[1].split("```")[0].strip()
            return json.loads(res_text)
        except Exception as e:
            st.error(f"Error en motor Google: {e}")
            pass

    return {
        "comp": "Error de conexión", "tienda": "N/A", "imp": "N/A", 
        "precio": 0, "moneda": "N/A", "um": "N/A", "link": "N/A", "vs": "Revisar API"
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
            status_text.text(f"🕵️ Investigando en Uruguay: {desc_actual[:35]}...")
            url_val = row[col_url] if col_url and pd.notna(row[col_url]) else None
            datos = ejecutar_analisis_ia(desc_actual, url_val)
            
            resultados.append({
                "Descripción Original": desc_actual,
                "Producto Competidor": datos.get('comp'),
                "Tienda": datos.get('tienda'),
                "Precio": datos.get('precio'),
                "Moneda": datos.get('moneda'),
                "Presentación": datos.get('um'),
                "Link Hallazgo": datos.get('link'),
                "Análisis de Reemplazo": datos.get('vs')
            })
    
    status_text.empty()
    progreso.empty()
    return resultados
