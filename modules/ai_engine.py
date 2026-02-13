import streamlit as st
import pandas as pd
import json
import re
import time
from google import genai
from google.genai import types
from groq import Groq

def ejecutar_analisis_ia(descripcion, url_ref=None):
    # Usamos tu nuevo prompt estratégico
    prompt = f"""
    Actúa como un Especialista en Inteligencia Competitiva y SEO Senior. 
    Tu objetivo es realizar un mapeo exhaustivo del ecosistema competitivo de la siguiente URL: {url_ref}
    Descripción de apoyo: "{descripcion}"

    Protocolo de análisis:
    1. IDENTIFICACIÓN DE CORE BUSINESS: Analiza la URL y define propuesta de valor, audiencia y keywords principales.
    2. COMPETENCIA DIRECTA (SERP Rivals): Identifica 5 sitios web en URUGUAY que compiten por el mismo producto/servicio.
    3. COMPETENCIA INDIRECTA/SUSTITUTOS: Identifica 3 sitios (blogs, foros o comparadores) que resuelven el mismo problema en Uruguay.
    4. ANÁLISIS DE BRECHA (Gap Analysis): Para los 3 competidores más fuertes, genera datos de: Nombre/URL, Ventaja Competitiva, y Estrategia de Contenidos.
    5. OPORTUNIDAD "BLUE OCEAN": Sugiere 2 ángulos de contenido para diferenciarse en el mercado uruguayo.

    IMPORTANTE: Verifica que los sitios están activos en 2026.
    Responde ESTRICTAMENTE en este formato JSON para que pueda procesarlo:
    {{
        "core_business": "Resumen de propuesta de valor",
        "keywords": ["key1", "key2"],
        "competidores_directos": [
            {{"nombre": "Nombre", "url": "URL", "ventaja": "Precio/Especialización", "contenido": "Estrategia"}}
        ],
        "competidores_indirectos": ["Sitio 1", "Sitio 2"],
        "blue_ocean": ["Oportunidad 1", "Oportunidad 2"]
    }}
    """

    if "GOOGLE_API_KEY" in st.secrets:
        try:
            client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
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
        except Exception: pass

    # Backup con Groq
    if "GROQ_API_KEY" in st.secrets:
        try:
            client_groq = Groq(api_key=st.secrets["GROQ_API_KEY"])
            completion = client_groq.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            return json.loads(completion.choices[0].message.content)
        except: pass

    return None

def procesar_lote_industrial(df):
    resultados_finales = []
    status_text = st.empty()
    
    col_desc = next((c for c in ['DESCRIPCION CORTA', 'Descripción'] if c in df.columns), df.columns[0])
    col_url = next((c for c in ['URL (Opcional pero recomendada)', 'URL', 'Link'] if c in df.columns), None)

    # Procesamos solo el primer artículo para esta prueba estratégica (o el lote completo)
    for index, row in df.iterrows():
        desc_actual = str(row[col_desc])
        url_val = row[col_url] if col_url and pd.notna(row[col_url]) else None
        
        if not url_val:
            continue

        status_text.info(f"🚀 Realizando Mapeo SEO & Competitivo: {desc_actual[:30]}...")
        data_ia = ejecutar_analisis_ia(desc_actual, url_val)
        
        if data_ia:
            # Por cada competidor directo encontrado, creamos una fila en el reporte
            for comp in data_ia.get("competidores_directos", []):
                resultados_finales.append({
                    "Producto Würth": desc_actual,
                    "Propuesta de Valor": data_ia.get("core_business"),
                    "Competidor": comp.get("nombre"),
                    "URL Competidor": comp.get("url"),
                    "Ventaja Competidor": comp.get("ventaja"),
                    "Estrategia Contenido": comp.get("contenido"),
                    "Oportunidad Blue Ocean": " / ".join(data_ia.get("blue_ocean", [])),
                    "Keywords": ", ".join(data_ia.get("keywords", []))
                })
        
        # Pausa para navegación profunda
        time.sleep(5)
            
    status_text.empty()
    return resultados_finales
