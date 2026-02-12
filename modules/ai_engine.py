import google.generativeai as genai
import openai
import streamlit as st
import json
import pandas as pd
import re
import time

def ejecutar_analisis_ia(descripcion, url_ref=None):
    desc_limpia = re.sub(r'\d{5,}', '', str(descripcion)).strip()
    
    prompt = f"""
    Eres un Investigador de Mercado en Uruguay. 
    Busca un reemplazo de OTRA MARCA para: "{desc_limpia}" en Uruguay.
    Ref técnica: {url_ref}

    Responde ESTRICTAMENTE en JSON:
    {{
        "comp": "Marca y modelo",
        "tienda": "Comercio en Uruguay",
        "precio": 0.0,
        "moneda": "USD/UYU",
        "link": "URL del producto en Uruguay",
        "vs": "Por qué es reemplazo"
    }}
    """

    # --- INTENTO CON OPENAI (Más estable para JSON) ---
    if "OPENAI_API_KEY" in st.secrets:
        try:
            client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                response_format={ "type": "json_object" }
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            st.warning(f"Error en OpenAI: {e}")

    # --- INTENTO CON GEMINI ---
    if "GOOGLE_API_KEY" in st.secrets:
        try:
            genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
            model = genai.GenerativeModel('gemini-1.5-pro')
            response = model.generate_content(prompt)
            res_text = response.text
            if "{" in res_text:
                res_text = res_text[res_text.find("{"):res_text.rfind("}")+1]
                return json.loads(res_text)
        except Exception as e:
            st.warning(f"Error en Gemini: {e}")

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
        status_text.text(f"🔎 Analizando {index + 1}/{total}: {desc_actual[:30]}")
        
        url_val = row[col_url] if col_url and pd.notna(row[col_url]) else None
        
        datos = ejecutar_analisis_ia(desc_actual, url_val)
        
        if datos:
            # Mostramos un pequeño aviso de éxito para confirmar que la IA respondió
            st.toast(f"✅ Hallazgo para: {desc_actual[:20]}", icon="🛒")
            resultados.append({
                "Descripción Original": desc_actual,
                "Producto Competidor": datos.get('comp', 'N/A'),
                "Tienda": datos.get('tienda', 'N/A'),
                "Precio": datos.get('precio', 0),
                "Moneda": datos.get('moneda', 'N/A'),
                "Link Hallazgo": datos.get('link', 'N/A'),
                "Análisis": datos.get('vs', 'N/A')
            })
        else:
            resultados.append({
                "Descripción Original": desc_actual,
                "Producto Competidor": "No hallado",
                "Tienda": "N/A", "Precio": 0, "Moneda": "N/A", "Link Hallazgo": "N/A", "Análisis": "Error de conexión"
            })
        
        time.sleep(1)
            
    status_text.empty()
    progreso.empty()
    return resultados
