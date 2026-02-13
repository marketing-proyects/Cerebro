import streamlit as st
import pandas as pd
import json
import re
import time
from google import genai
from google.genai import types
from groq import Groq

def ejecutar_analisis_ia(descripcion, url_ref=None):
    desc_limpia = str(descripcion).strip()
    
    # PROMPT DE EXTRACCIÓN Y BÚSQUEDA MULTI-COMPETIDOR
    prompt = f"""
    ERES UN INGENIERO DE PRODUCTO Y ANALISTA DE MERCADO EN URUGUAY.
    
    PASO 1: EXTRACCIÓN DE ADN TÉCNICO
    Analiza profundamente la URL: {url_ref} y la descripción: "{desc_limpia}".
    Define: ¿Qué es el objeto? ¿De qué material está hecho? ¿Para qué máquina o proceso sirve exactamente?
    (Si es un cabezal de desmalezadora, NO puede ser un adhesivo químico).

    PASO 2: BÚSQUEDA DIRIGIDA EN URUGUAY (google.com.uy)
    Busca competidores que cumplan la MISMA función técnica en importadores relevantes de Uruguay: 
    Salvador Livio, Ingco Uruguay, Pampin, Orofino, Sodimac, Mercado Libre UY.

    PASO 3: FILTRO DE ALUCINACIÓN
    Si el competidor hallado no sirve para la misma máquina o proceso que el original, descártalo.

    INSTRUCCIÓN DE SALIDA:
    Debes encontrar AL MENOS 3 COMPETIDORES DISTINTOS.
    Responde ESTRICTAMENTE en este formato JSON (Lista de objetos):
    {{
        "adn_tecnico": "Breve descripción técnica que entendiste del original",
        "competidores": [
            {{
                "comp": "Nombre completo del competidor 1",
                "marca": "Marca",
                "presentacion": "Medidas/Empaque",
                "precio": 0.0,
                "moneda": "USD/UYU",
                "importador": "Importador en Uruguay",
                "distribuidor": "Punto de venta",
                "calidad": "Premium/Media/Económica",
                "link": "URL del hallazgo en Uruguay",
                "vs": "Comparativa técnica vs original"
            }},
            {{ "..." }},
            {{ "..." }}
        ]
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

    # Respaldo Groq (Llama 3.3)
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
    progreso = st.progress(0)
    
    col_desc = next((c for c in ['DESCRIPCION CORTA', 'Descripción'] if c in df.columns), df.columns[0])
    col_url = next((c for c in ['URL (Opcional pero recomendada)', 'URL', 'Link'] if c in df.columns), None)

    total = len(df)
    for index, row in df.iterrows():
        pct = (index + 1) / total
        progreso.progress(pct)
        
        desc_actual = str(row[col_desc])
        status_text.info(f"🧬 Extrayendo ADN y buscando competidores: {desc_actual[:30]}...")
        
        url_val = row[col_url] if col_url and pd.notna(row[col_url]) else None
        
        # Llamada a la IA (devuelve una lista de competidores)
        data_ia = ejecutar_analisis_ia(desc_actual, url_val)
        
        if data_ia and "competidores" in data_ia:
            adn = data_ia.get("adn_tecnico", "N/A")
            for c in data_ia["competidores"]:
                resultados_finales.append({
                    "Original (Würth)": desc_actual,
                    "ADN Identificado": adn,
                    "Competidor": c.get('comp'),
                    "Marca": c.get('marca'),
                    "Presentación": c.get('presentacion'),
                    "Precio": c.get('precio'),
                    "Moneda": c.get('moneda'),
                    "Importador": c.get('importador'),
                    "Distribuidor": c.get('distribuidor'),
                    "Calidad": c.get('calidad'),
                    "Link": c.get('link'),
                    "Análisis": c.get('vs')
                })
        else:
            # Fila de error si no encuentra nada
            resultados_finales.append({
                "Original (Würth)": desc_actual,
                "ADN Identificado": "Error de identificación",
                "Competidor": "No hallado", "Marca": "N/A", "Precio": 0, "Moneda": "N/A",
                "Importador": "N/A", "Distribuidor": "N/A", "Calidad": "N/A", "Link": "N/A", "Análisis": "Revisar API"
            })
        
        time.sleep(3) # Pausa aumentada para permitir 3 búsquedas profundas por producto
            
    status_text.empty()
    progreso.empty()
    return resultados_finales
