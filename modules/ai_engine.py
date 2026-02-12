import google.generativeai as genai
import openai
import streamlit as st
import json
import pandas as pd
import re

def ejecutar_analisis_ia(descripcion, url_ref=None):
    # LIMPIEZA: Borramos códigos de más de 5 dígitos para que la IA no se confunda
    desc_limpia = re.sub(r'\d{5,}', '', str(descripcion)).strip()
    
    prompt = f"""
    Eres un Investigador Senior de Mercado en Uruguay. 
    Tu misión es encontrar un producto COMPETIDOR local en Uruguay para: "{desc_limpia}"

    REGLAS ESTRICTAS:
    1. ANALIZA LA URL: Si es de España, entra y entiende la función técnica.
    2. BUSCA EN URUGUAY: Usa Mercado Libre UY, Sodimac o ferreterías industriales locales.
    3. MARCAS EQUIVALENTES: Si no hay Würth, busca Sika, Fischer, 3M, Loctite, Stanley o Bosch.
    4. RESPUESTA: No acepto "No encontrado". Si no hay precio exacto, busca el del equivalente funcional más cercano en Uruguay.

    Responde ESTRICTAMENTE en este formato JSON:
    {{
        "comp": "Marca y modelo competidor",
        "tienda": "Tienda en Uruguay",
        "imp": "Marca local",
        "precio": 0.0,
        "moneda": "USD/UYU",
        "um": "Presentación",
        "link": "URL del hallazgo en Uruguay",
        "vs": "Breve comparativa técnica"
    }}
    """

    # --- MOTOR GEMINI (PRIORIDAD) ---
    if "GOOGLE_API_KEY" in st.secrets:
        try:
            genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
            model = genai.GenerativeModel('gemini-1.5-pro')
            response = model.generate_content(prompt)
            res_text = response.text.replace('```json', '').replace('```', '').strip()
            return json.loads(res_text)
        except:
            pass

    # --- FALLBACK SEGURO ---
    return {
        "comp": "Buscando...", 
        "tienda": "Pendiente", 
        "imp": "N/A", 
        "precio": 0, 
        "moneda": "N/A", 
        "um": "N/A", 
        "link": "N/A", 
        "vs": f"Análisis de {desc_limpia}"
    }

def procesar_lote_industrial(df):
    resultados = []
    status_text = st.empty()
    progreso = st.progress(0)
    
    # Identificación de columnas
    col_desc = next((c for c in ['DESCRIPCION CORTA', 'Descripción'] if c in df.columns), df.columns[1])
    col_url = next((c for c in ['URL (Opcional pero recomendada)', 'URL', 'Link'] if c in df.columns), None)

    total = len(df)
    for index, row in df.iterrows():
        pct = (index + 1) / total
        progreso.progress(pct)
        
        desc_actual = str(row[col_desc])
        if pd.notna(row[col_desc]) and desc_actual.lower() != 'none' and desc_actual.strip() != '':
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
