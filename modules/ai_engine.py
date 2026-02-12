import google.generativeai as genai
import openai
import streamlit as st
import json
import pandas as pd
import re

def ejecutar_analisis_ia(descripcion, url_ref=None):
    # LIMPIEZA AGRESIVA: Eliminamos cualquier código numérico de la descripción
    # Esto evita que la IA se pierda buscando números de parte de Würth
    desc_para_ia = re.sub(r'\d+', '', str(descripcion)).strip()
    
    prompt = f"""
    Eres un Investigador Senior de Mercado en Uruguay. 
    Tu objetivo es encontrar un producto COMPETIDOR en Uruguay para: "{desc_para_ia}".

    DATOS TÉCNICOS:
    - ADN del producto: {desc_para_ia}
    - URL de referencia: {url_ref}

    Misión:
    1. Analiza la URL para entender la composición química o mecánica (ej: es un adhesivo MS, es un disco de corte Inox).
    2. Busca en el mercado uruguayo (Mercado Libre UY, Sodimac, Ferreterías Industriales).
    3. Identifica marcas equivalentes: Sika, Fischer, 3M, Loctite, Stanley, Bosch.
    4. NO respondas "No encontrado". Si no hay precio exacto, busca el de un producto con la misma función en Uruguay.

    Responde en JSON:
    {{
        "comp": "Marca y modelo competidor",
        "tienda": "Tienda en Uruguay",
        "imp": "Marca local",
        "precio": 0.0,
        "moneda": "USD/UYU",
        "um": "Presentación",
        "link": "URL del hallazgo",
        "vs": "Comparativa técnica",
        "obs": "Notas"
    }}
    """

    # --- MOTOR GEMINI (GRATUITO) ---
    if "GOOGLE_API_KEY" in st.secrets:
        try:
            genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
            model = genai.GenerativeModel('gemini-1.5-pro')
            response = model.generate_content(prompt)
            res_text = response.text.replace('```json', '').replace('```', '').strip()
            return json.loads(res_text)
        except:
            pass

    return {{
        "comp": "Buscando equivalencia...", "tienda": "Google UY", "imp": "N/A", 
        "precio": 0, "moneda": "N/A", "um": "N/A", "link": "N/A", 
        "vs": f"Analizando {desc_para_ia}", "obs": "Reintentar"
    }}

def procesar_lote_industrial(df):
    resultados = []
    status_text = st.empty()
    progreso = st.progress(0)
    
    # Identificamos columnas ignorando "CODIGO"
    col_desc = next((c for c in ['DESCRIPCION CORTA', 'Descripción'] if c in df.columns), df.columns[1])
    col_url = next((c for c in ['URL (Opcional pero recomendada)', 'URL', 'Link'] if c in df.columns), None)

    # Convertimos a lista para asegurar que procesamos TODAS las filas que tengan descripción
    total = len(df)
    for index, row in df.iterrows():
        pct = (index + 1) / total
        progreso.progress(pct)
        
        # Validamos que la descripción no esté vacía (ignoramos el código)
        desc_actual = str(row[col_desc])
        if desc_actual.lower() != 'none' and desc_actual.strip() != '':
            status_text.text(f"🕵️ Investigando {index + 1} de {total}: {desc_actual[:30]}...")
            
            url_val = row[col_url] if col_url and pd.notna(row[col_url]) else None
            datos = ejecutar_analisis_ia(desc_actual, url_val)
            
            resultados.append({
                "Descripción Original": desc_actual,
                "Producto Competidor": datos.get('comp'),
                "Tienda (Venta)": datos.get('tienda'),
                "Precio": datos.get('precio'),
                "Moneda": datos.get('moneda'),
                "Link Hallazgo": datos.get('link'),
                "Análisis vs Würth": datos.get('vs')
            })
    
    status_text.empty()
    progreso.empty()
    return resultados
