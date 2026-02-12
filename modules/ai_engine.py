import google.generativeai as genai
import openai
import streamlit as st
import json
import pandas as pd

def ejecutar_analisis_ia(descripcion, url_ref=None):
    prompt = f"""
    Objetivo: Investigador experto de Mercados para Uruguay.
    Analiza: {descripcion} 
    URL: {url_ref}
    Responde estrictamente en JSON con campos: comp, tienda, imp, precio, moneda, um, link, vs.
    """

    # --- INTENTO 1: GEMINI ---
    if "GOOGLE_API_KEY" in st.secrets:
        try:
            genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
            model = genai.GenerativeModel('gemini-1.5-pro')
            response = model.generate_content(prompt)
            res_text = response.text.replace('```json', '').replace('```', '').strip()
            return json.loads(res_text)
        except:
            pass

    # --- INTENTO 2: OPENAI ---
    if "OPENAI_API_KEY" in st.secrets:
        try:
            client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                response_format={ "type": "json_object" }
            )
            return json.loads(response.choices[0].message.content)
        except:
            pass
    
    # SI TODO FALLA, DEVOLVEMOS UN OBJETO VACÍO SEGURO
    return {"comp": "No encontrado", "tienda": "N/A", "imp": "N/A", "precio": 0, "moneda": "N/A", "um": "N/A", "link": "N/A", "vs": "N/A"}

def procesar_lote_industrial(df):
    resultados = []
    status_text = st.empty()
    progreso = st.progress(0)
    
    col_desc = next((c for c in ['DESCRIPCION CORTA', 'Descripción', 'Especificación'] if c in df.columns), df.columns[0])
    col_url = next((c for c in ['URL', 'Enlace', 'Link'] if c in df.columns), None)

    total = len(df)
    for index, row in df.iterrows():
        pct = (index + 1) / total
        progreso.progress(pct)
        status_text.text(f"Analizando {index + 1} de {total}...")
        
        if pd.notna(row[col_desc]):
            url_val = row[col_url] if col_url else None
            datos = ejecutar_analisis_ia(row[col_desc], url_val)
            # Siempre agregamos algo a la lista para que no quede vacía
            resultados.append({
                "Descripción Original": row[col_desc],
                "Competidor": datos.get('comp'),
                "Tienda": datos.get('tienda'),
                "Precio": datos.get('precio'),
                "Moneda": datos.get('moneda'),
                "Link Hallazgo": datos.get('link'),
                "Análisis": datos.get('vs')
            })
    
    status_text.empty()
    progreso.empty()
    return resultados
