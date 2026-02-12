import google.generativeai as genai
import openai
import streamlit as st
import json
import pandas as pd
import re
import time

def ejecutar_analisis_ia(descripcion, url_ref=None):
    # Limpieza de SKUs para no confundir la búsqueda técnica
    desc_limpia = re.sub(r'\d{5,}', '', str(descripcion)).strip()
    
    # TU METODOLOGÍA DE INVESTIGACIÓN AL 100%
    prompt = f"""
    Eres un Investigador Senior de Compras Industriales en Uruguay. Tu misión es encontrar el reemplazo ideal para un producto.

    ARTÍCULO A ANALIZAR: "{desc_limpia}"
    URL DE REFERENCIA: {url_ref}

    METODOLOGÍA DE INVESTIGACIÓN OBLIGATORIA:
    1. IDENTIFICACIÓN TÉCNICA: Analiza la descripción y la URL. Identifica qué es el producto (ej. Adhesivo de polímero MS, Tornillo hexagonal grado 8, etc.). Ignora que la URL sea de una marca específica o de otro lugar distinto a Uruguay; úsala solo para extraer especificaciones (medidas, químicos, resistencias).
    
    2. BÚSQUEDA DE COMPETENCIA EN URUGUAY: Busca activamente en Google Uruguay, Mercado Libre Uruguay, Sodimac Uruguay, Ingco Uruguay, Salvador Livio Uruguay, Pampin Uruguay, y otros proveedores industriales y no industriales locales.
    
    3. SELECCIÓN DE COMPETIDOR: Debes encontrar productos de OTRAS MARCAS (distintas a la marca cargada en el excel inicial) que se vendan actualmente en Uruguay y que sean el reemplazo directo de cada artículo. No acepto como competidor la misma marca del archivo original.
    
    4. DATA EXTRACTION: Obtén el precio real de mercado (en UYU o USD), la tienda que lo vende y el link directo a la publicación en Uruguay.

    RESPONDE ESTRICTAMENTE EN ESTE FORMATO JSON:
    {{
        "comp": "Marca y modelo del competidor",
        "tienda": "Nombre del comercio o proveedor en Uruguay",
        "imp": "Importador / Distribuidor local",
        "precio": 0.0,
        "moneda": "USD/UYU",
        "um": "Presentación (ej. 310ml, Pack x100)",
        "link": "URL directa de la publicación en Uruguay",
        "vs": "Análisis de reemplazo: por qué este producto sustituye al original"
    }}
    """

    # --- MOTOR 1: GEMINI (Especialista en Búsqueda) ---
    if "GOOGLE_API_KEY" in st.secrets:
        try:
            genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
            model = genai.GenerativeModel('gemini-1.5-pro')
            response = model.generate_content(prompt)
            res_text = response.text
            if "{" in res_text:
                res_text = res_text[res_text.find("{"):res_text.rfind("}")+1]
                return json.loads(res_text)
        except:
            pass

    # --- MOTOR 2: OPENAI GPT-4o (Especialista en Precisión) ---
    if "OPENAI_API_KEY" in st.secrets:
        try:
            client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
            response_oa = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                response_format={ "type": "json_object" }
            )
            return json.loads(response_oa.choices[0].message.content)
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
        if pd.notna(row[col_desc]) and desc_actual.lower() != 'none':
            status_text.text(f"🕵️ Investigando en Uruguay: {desc_actual[:35]}...")
            
            url_val = row[col_url] if col_url and pd.notna(row[col_url]) else None
            
            # Ejecución Multi-IA
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
                    "Producto Competidor": "No hallado",
                    "Tienda": "N/A", "Precio": 0, "Moneda": "N/A", "Link Hallazgo": "N/A", "Análisis de Reemplazo": "Sin resultados tras búsqueda Multi-IA"
                })
            
            # Pausa de seguridad para evitar errores de cuota (Rate Limit)
            time.sleep(2)
            
    status_text.empty()
    progreso.empty()
    return resultados
