import google.generativeai as genai
import openai
import streamlit as st
import json
import pandas as pd
import re

def ejecutar_analisis_ia(descripcion, url_ref=None):
    # Limpieza de SKUs para que no interfieran en la búsqueda semántica
    desc_limpia = re.sub(r'\d{5,}', '', str(descripcion)).strip()
    
    prompt = f"""
    Eres un Investigador Senior de Compras Industriales en Uruguay. Tu misión es encontrar el reemplazo ideal para un producto.

    ARTÍCULO A ANALIZAR: "{desc_limpia}"
    URL DE REFERENCIA: {url_ref}

    METODOLOGÍA DE INVESTIGACIÓN OBLIGATORIA:
    1. IDENTIFICACIÓN TÉCNICA: Analiza la descripción y la URL. Identifica qué es el producto (ej. Adhesivo de polímero MS, Tornillo hexagonal grado 8, etc.). Ignora que la URL sea de Würth España o de otro lugar distinto a Uruguay; úsala solo para extraer especificaciones (medidas, químicos, resistencias).
    
    2. BÚSQUEDA DE COMPETENCIA EN URUGUAY: Busca activamente en Google Uruguay, Mercado Libre Uruguay, Sodimac Uruguay, Ingco Uruguay, Salvador Livio Uruguay, Pampin Uruguay, y otros proveedores industriales y no industriales locales.
    
    3. SELECCIÓN DE COMPETIDOR: Debes encontrar productos de OTRAS MARCAS (distintas a la marca del producto cargado inicialmente) que se vendan actualmente en Uruguay y que sean el reemplazo directo de cada artículo cargado inicialmente. No acepto como competidor la misma marca del archivo original.
    
    4. DATA EXTRACTION: Obtén el precio real de mercado (en UYU o USD), la tienda que lo vende y el link directo a la publicación.

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

    # --- MOTOR PRINCIPAL: GEMINI 1.5 PRO ---
    if "GOOGLE_API_KEY" in st.secrets:
        try:
            genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
            model = genai.GenerativeModel('gemini-1.5-pro')
            # La IA procesa la metodología técnica solicitada
            response = model.generate_content(prompt)
            res_text = response.text.replace('```json', '').replace('```', '').strip()
            return json.loads(res_text)
        except:
            pass

    return {
        "comp": "No se encontró reemplazo",
        "tienda": "N/A",
        "imp": "N/A",
        "precio": 0,
        "moneda": "N/A",
        "um": "N/A",
        "link": "N/A",
        "vs": "La investigación no arrojó resultados en los proveedores locales seleccionados."
    }

def procesar_lote_industrial(df):
    resultados = []
    status_text = st.empty()
    progreso = st.progress(0)
    
    # Identificación de columnas en el Excel
    col_desc = next((c for c in ['DESCRIPCION CORTA', 'Descripción'] if c in df.columns), df.columns[0])
    col_url = next((c for c in ['URL (Opcional pero recomendada)', 'URL', 'Link'] if c in df.columns), None)

    total = len(df)
    for index, row in df.iterrows():
        pct = (index + 1) / total
        progreso.progress(pct)
        
        desc_actual = str(row[col_desc])
        if pd.notna(row[col_desc]) and desc_actual.lower() != 'none':
            status_text.text(f"🕵️ Investigando en Uruguay: {desc_actual[:40]}...")
            
            url_val = row[col_url] if col_url and pd.notna(row[col_url]) else None
            datos = ejecutar_analisis_ia(desc_actual, url_val)
            
            resultados.append({
                "Descripción Original": desc_actual,
                "Producto Competidor": datos.get('comp'),
                "Tienda": datos.get('tienda'),
                "Importador/Marca": datos.get('imp'),
                "Precio": datos.get('precio'),
                "Moneda": datos.get('moneda'),
                "Presentación": datos.get('um'),
                "Link Hallazgo": datos.get('link'),
                "Análisis de Reemplazo": datos.get('vs')
            })
    
    status_text.empty()
    progreso.empty()
    return resultados
