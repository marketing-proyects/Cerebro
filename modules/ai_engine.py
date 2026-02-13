import streamlit as st
import pandas as pd
import json
import re
import time
from google import genai
from google.genai import types
from groq import Groq

def ejecutar_analisis_ia(descripcion, url_ref=None):
    # Limpieza: eliminamos cualquier residuo numérico para que la IA se enfoque en la semántica
    desc_limpia = str(descripcion).strip()
    
    prompt = f"""
    ERES UN ANALISTA SUPER SENIOR DE INTELIGENCIA DE MERCADO URUGUAYO. HOY DEBES BUSCAR TODO LO QUE COMPITA CON LOS ARTICULOS QUE TE HE PROPORCIONADO.
    
    PRODUCTO ORIGINAL: "{desc_limpia}"
    URL DE REFERENCIA TÉCNICA: {url_ref}

    TU MISIÓN (CRÍTICA):
    1. IDENTIFICACIÓN TÉCNICA PROFUNDA: Analiza la URL y la Descripción. Identifica la naturaleza exacta del producto (químico, abrasivo, fijación, etc.). 
       IMPORTANTE: No te dejes guiar por códigos internos; la URL es la fuente de verdad técnica.
    
    2. BÚSQUEDA DE COMPETIDORES EN URUGUAY: Localiza en proveedores locales (Mercado Libre UY, Ingco, Salvador Livio, Pampin, Sodimac, Orofino, etc.) 
       productos de OTRAS MARCAS que realicen la MISMA FUNCIÓN TÉCNICA.
    
    3. CADENA DE VALOR: Identifica el Importador y el Distribuidor/Punto de Venta en Uruguay.
    
    4. POSICIONAMIENTO DE MERCADO: Clasifica la 'Calidad Percibida' en tres niveles: 'Premium' (Líderes), 'Media' (Profesional estándar) o 'Económica' (Bajo costo).

    Responde ESTRICTAMENTE en este formato JSON:
    {{
        "comp": "Nombre completo del producto competidor",
        "marca": "Marca del competidor",
        "presentacion": "Unidad de empaque/medida (ej. 310ml, Pack x100)",
        "precio": 0.0,
        "moneda": "USD/UYU",
        "importador": "Importador legal en Uruguay",
        "distribuidor": "Punto de venta / Distribuidor local",
        "calidad": "Premium / Media / Económica",
        "link": "URL del hallazgo en Uruguay",
        "analisis_tecnico": "Comparativa de rendimiento vs original"
    }}
    """

    # --- MOTOR PRINCIPAL: GEMINI 2.0 (Con Búsqueda de Google Activa) ---
    if "GOOGLE_API_KEY" in st.secrets:
        try:
            client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
            # Herramienta de búsqueda para obtener precios reales y proveedores en Uruguay
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

    # --- RESPALDO: GROQ (Si Gemini falla o alcanza límites de cuota) ---
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
    
    # Identificación de columnas dinámicas
    col_desc = next((c for c in ['DESCRIPCION CORTA', 'Descripción'] if c in df.columns), df.columns[0])
    col_url = next((c for c in ['URL (Opcional pero recomendada)', 'URL', 'Link'] if c in df.columns), None)

    total = len(df)
    for index, row in df.iterrows():
        pct = (index + 1) / total
        progreso.progress(pct)
        
        desc_actual = str(row[col_desc])
        # Procesamos todo lo que tenga descripción, sin importar si el código es "None"
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
                    "Análisis Técnico": datos.get('analisis_tecnico')
                })
            
            # Pausa de seguridad para respetar las cuotas de búsqueda de Google
            time.sleep(2)
            
    status_text.empty()
    progreso.empty()
    return resultados
