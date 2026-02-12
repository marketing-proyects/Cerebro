from google import genai
from google.genai import types
from groq import Groq
import streamlit as st
import json
import re
import time
import requests

def ejecutar_analisis_ia(descripcion, url_ref=None):
    desc_limpia = re.sub(r'\d{5,}', '', str(descripcion)).strip()
    
    prompt = f"""
    Eres un Investigador Senior de Compras Industriales en Uruguay.
    ARTÍCULO: "{desc_limpia}"
    URL REFERENCIA: {url_ref}

    METODOLOGÍA:
    1. IDENTIFICACIÓN TÉCNICA: Usa la descripción y URL para entender medidas y función.
    2. BÚSQUEDA URUGUAY: Busca en Google Uruguay resultados de Sodimac, Mercado Libre UY, Ingco, Salvador Livio o Pampin.
    3. SELECCIÓN: Encuentra una marca de reemplazo (Sika, 3M, Fischer, Bosch, Ingco) disponible en Uruguay.
    4. DATA EXTRACTION: Obtén precio real, tienda y link directo.

    Responde ESTRICTAMENTE en JSON:
    {{
        "comp": "Marca y modelo",
        "tienda": "Tienda en Uruguay",
        "precio": 0.0,
        "moneda": "USD/UYU",
        "um": "Presentación",
        "link": "URL en Uruguay",
        "vs": "Análisis de reemplazo"
    }}
    """

    # --- 1. MOTOR PRINCIPAL: GEMINI (Tu cuenta personal con nueva librería) ---
    if "GOOGLE_API_KEY" in st.secrets:
        try:
            client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
            # Usamos búsqueda de Google activa
            search_tool = types.Tool(google_search=types.GoogleSearch())
            
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
                config=types.GenerateContentConfig(tools=[search_tool])
            )
            
            res_text = response.text
            if "{" in res_text:
                res_text = res_text[res_text.find("{"):res_text.rfind("}")+1]
                return json.loads(res_text)
        except Exception as e:
            st.warning(f"Gemini en espera, saltando a respaldo...")

    # --- 2. RESPALDO: GROQ (Llama 3) ---
    if "GROQ_API_KEY" in st.secrets:
        try:
            client_groq = Groq(api_key=st.secrets["GROQ_API_KEY"])
            completion = client_groq.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            return json.loads(completion.choices[0].message.content)
        except:
            pass

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
        status_text.info(f"🕵️ Investigando {index+1}/{total}: {desc_actual[:30]}")
        
        url_val = row[col_url] if col_url and pd.notna(row[col_url]) else None
        datos = ejecutar_analisis_ia(desc_actual, url_val)
        
        if datos:
            resultados.append({
                "Descripción Original": desc_actual,
                "Producto Competidor": datos.get('comp'),
                "Tienda": datos.get('tienda'),
                "Precio": datos.get('precio'),
                "Moneda": datos.get('moneda'),
                "Link Hallazgo": datos.get('link'),
                "Análisis de Reemplazo": datos.get('vs')
            })
        else:
            resultados.append({
                "Descripción Original": desc_actual,
                "Producto Competidor": "Sin resultados", "Tienda": "N/A", "Precio": 0, "Moneda": "N/A", "Link Hallazgo": "N/A", "Análisis de Reemplazo": "Error en investigación"
            })
        time.sleep(1) # Fluidez
            
    status_text.empty()
    progreso.empty()
    return resultados
