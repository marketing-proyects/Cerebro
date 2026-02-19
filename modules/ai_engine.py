import streamlit as st
import pandas as pd
import json
import time
from google import genai
from google.genai import types
from groq import Groq

def ejecutar_analisis_ia(descripcion, url_ref=None):
    desc_limpia = str(descripcion).strip()
    
    # Limpiamos la URL para que Gemini no tire Error 400 si está vacía o es 'nan'
    if not url_ref or str(url_ref).lower() == "nan":
        url_limpia = "No disponible (buscar usando solo la descripción)"
    else:
        url_limpia = str(url_ref).strip()
    
    # NUEVO PROMPT: PROTOCOLO DE INTELIGENCIA COMPETITIVA & SEO SENIOR
    prompt = f"""
    Actúa como un Especialista en Inteligencia Competitiva y SEO Senior en Uruguay. 
    Tu objetivo es realizar un mapeo exhaustivo del ecosistema competitivo del siguiente producto/URL: {url_limpia}
    Descripción base: "{desc_limpia}"

    PROTOCOLO DE ANÁLISIS (ESTRICTO):

    1. IDENTIFICACIÓN DE ADN TÉCNICO: Define qué es el objeto, materiales, audiencia objetivo y para qué máquina o proceso sirve exactamente. 
       (IMPORTANTE: Si la URL es un accesorio mecánico, NO puede ser un químico).

    2. COMPETENCIA DIRECTA (SERP Rivals): Identifica 3 empresas en URUGUAY que importen o vendan exactamente el mismo producto/servicio (ej. Salvador Livio, Ingco, Pampin, Orofino, Sodimac).

    3. ANÁLISIS DE MERCADO URUGUAY: Para cada competidor detectado, investiga:
       - Importador: Quién introduce la marca al país (ej. DT Importaciones, Edintor, etc.).
       - Precios: Estima el precio mayorista (B2B) y minorista (PVP).
       - Estrategia Comercial: ¿Es liderazgo en costo? ¿Especialización técnica? ¿Omnicanalidad?
       - Pirámide de Calidad: Clasifícalo en 'Premium', 'Media' o 'Económica'.

    4. COMPETENCIA INDIRECTA: Identifica sitios que resuelven el mismo problema (ej. blogs técnicos o comparadores).

    5. OPORTUNIDAD "BLUE OCEAN": Sugiere 2 nichos o ángulos de contenido que Würth Uruguay podría explotar.

    IMPORTANTE: Verifica que los sitios están activos en 2026. 
    Responde ESTRICTAMENTE en este formato JSON (Lista de competidores):
    {{
        "adn_tecnico": "Propuesta de valor y descripción técnica que entendiste",
        "keywords_principales": ["key1", "key2"],
        "mapeo_competitivo": [
            {{
                "nombre_competidor": "Nombre",
                "marca": "Marca",
                "importador": "Importador legal en Uruguay",
                "presentacion": "Unidad/Empaque",
                "precio_mayorista": 0.0,
                "precio_minorista": 0.0,
                "moneda": "USD/UYU",
                "estrategia_comercial": "Descripción de su táctica de ventas",
                "calidad_percibida": "Premium/Media/Económica",
                "url_evidencia": "Link activo en Uruguay",
                "analisis_gap": "Ventaja competitiva vs Würth"
            }}
        ],
        "blue_ocean": ["Oportunidad 1", "Oportunidad 2"]
    }}
    """

    error_api = ""
    
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
        except Exception as e: 
            error_api = f"Gemini Falló: {str(e)[:50]}"

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
        except Exception as e: 
            if error_api:
                error_api += f" | Groq Falló: {str(e)[:50]}"
            else:
                error_api = f"Groq Falló: {str(e)[:50]}"
                
    # Si ambas fallan, enviamos el aviso a la pantalla para monitoreo
    if error_api:
        st.toast(f"⏳ Límite de API alcanzado o error. Detalle: {error_api}", icon="⚠️")

    return None

def procesar_lote_industrial(df):
    resultados_finales = []
    status_text = st.empty()
    progreso = st.progress(0)
    
    # Lectura original de columnas
    col_desc = next((c for c in ['DESCRIPCION CORTA', 'Descripción'] if c in df.columns), df.columns[0])
    col_url = next((c for c in ['URL (Opcional pero recomendada)', 'URL', 'Link'] if c in df.columns), None)

    total = len(df)
    for index, row in df.iterrows():
        pct = (index + 1) / total
        progreso.progress(pct)
        
        desc_actual = str(row[col_desc])
        url_val = row[col_url] if col_url and pd.notna(row[col_url]) else None
        
        # Filtro original: se salta el producto si no tiene URL en el Excel
        if not url_val or str(url_val).lower() == "nan":
            continue

        status_text.info(f"🚀 Mapeo Estratégico & ADN: {desc_actual[:30]}...")
        data_ia = ejecutar_analisis_ia(desc_actual, url_val)
        
        if data_ia and "mapeo_competitivo" in data_ia:
            adn = data_ia.get("adn_tecnico", "N/A")
            for comp in data_ia["mapeo_competitivo"]:
                resultados_finales.append({
                    "Original (Würth)": desc_actual,
                    "ADN Identificado": adn,
                    "Competidor": comp.get("nombre_competidor"),
                    "Marca": comp.get("marca"),
                    "Importador": comp.get("importador"),
                    "Presentación": comp.get("presentacion"),
                    "P. Mayorista": comp.get("precio_mayorista"),
                    "P. Minorista": comp.get("precio_minorista"),
                    "Moneda": comp.get("moneda"),
                    "Estrategia": comp.get("estrategia_comercial"),
                    "Calidad": comp.get("calidad_percibida"),
                    "Gap vs Würth": comp.get("analisis_gap"),
                    "Link": comp.get("url_evidencia")
                })
        
        time.sleep(5) # Pausa original para cuidar el límite de uso de las APIs
            
    status_text.empty()
    progreso.empty()
    return resultados_finales
