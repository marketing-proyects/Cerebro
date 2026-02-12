import streamlit as st
import pandas as pd
import json
import re
import time
from google import genai
from google.genai import types
from groq import Groq

def ejecutar_analisis_ia(descripcion, url_ref=None):
    # Limpiamos cualquier código numérico sobrante para no sesgar la búsqueda
    desc_limpia = re.sub(r'\d{5,}', '', str(descripcion)).strip()
    
    prompt = f"""
    ERES UN ANALISTA DE INTELIGENCIA COMERCIAL PARA EL MERCADO INDUSTRIAL EN URUGUAY.
    
    OBJETO DE ESTUDIO: "{desc_limpia}"
    URL DE FICHA TÉCNICA: {url_ref}

    METODOLOGÍA DE INVESTIGACIÓN DE CAMPO:
    1. PRIORIDAD TÉCNICA: Analiza la descripción y extrae datos de la URL (medidas, composición, uso). No importa si la URL es de otro país, úsala para identificar el producto exacto.
    2. BÚSQUEDA URUGUAY: Localiza productos de OTRAS MARCAS (Sika, 3M, Fischer, Bosch, Stanley, etc.) disponibles en Uruguay.
    3. CADENA DE VALOR: Identifica quién es el Importador y quién el Distribuidor (si es el mismo, repite el nombre).
    4. POSICIONAMIENTO: Clasifica la Calidad Percibida en: 'Premium', 'Media' o 'Económica'.

    Responde ESTRICTAMENTE en este formato JSON:
    {{
        "comp": "Marca y Modelo Competidor",
        "marca": "Marca",
        "presentacion": "Unidad de empaque (ej. 310ml, Pack x100)",
        "precio": 0.0,
        "moneda": "USD/UYU",
        "importador": "Nombre del Importador en Uruguay",
        "distribuidor": "Punto de venta / Distribuidor",
        "calidad": "Premium / Media / Económica",
        "link": "URL del hallazgo en Uruguay",
        "analisis_vs": "Diferencia técnica clave con el original"
    }}
    """

    # --- MOTOR PRINCIPAL: GEMINI 2.0 (Con Búsqueda de Google) ---
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
        except Exception:
            pass

    # --- RESPALDO: GROQ (Si Gemini falla o se satura) ---
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
    
    # Identificación de columnas (No dependemos del Código)
    col_desc = next((c for c in ['DESCRIPCION CORTA', 'Descripción'] if c in df.columns), df.columns[0])
    col_url = next((c for c in ['URL (Opcional pero recomendada)', 'URL', 'Link'] if c in df.columns), None)

    total = len(df)
    for index, row in df.iterrows():
        pct = (index + 1) / total
        progreso.progress(pct)
        
        desc_actual = str(row[col_desc])
        # Procesamos aunque el código sea "None" o vacío
        if pd.notna(row[col_desc]) and desc_actual.lower() != 'none':
            status_text.info(f"🕵️ Investigando Mercado UY: {desc_actual[:35]}...")
            
            url_val = row[col_url] if col_url and pd.notna(row[col_url]) else None
            datos = ejecutar_analisis_ia(desc_actual, url_val)
            
            if datos:
                resultados.append({
                    "Descripción Original": desc_actual,
                    "Competidor": datos.get('comp'),
                    "Marca": datos.get('marca'),
                    "Presentación": datos.get('presentacion'),
                    "Precio": datos.get('precio'),
                    "Moneda": datos.get('moneda'),
                    "Importador": datos.get('importador'),
                    "Distribuidor": datos.get('distribuidor'),
                    "Calidad": datos.get('calidad'),
                    "Link": datos.get('link'),
                    "Análisis": datos.get('analisis_vs')
                })
            
            time.sleep(1.5) # Pausa técnica para estabilidad
            
    status_text.empty()
    progreso.empty()
    return resultados
