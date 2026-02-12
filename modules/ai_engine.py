import google.generativeai as genai
import openai
import streamlit as st
import json
import pandas as pd

def ejecutar_analisis_ia(descripcion, url_ref=None):
    prompt = f"""
    Eres un Investigador Forense de Mercados para Würth Uruguay. 
    Tu misión es encontrar competencia local basada en ADN técnico.

    PRODUCTO: {descripcion}
    URL REFERENCIA: {url_ref}

    INSTRUCCIONES:
    1. Analiza la URL (incluso si es de España) para entender la química o mecánica. 
    2. Busca equivalentes en Uruguay (Mercado Libre UY, Sodimac, Ferreterías Industriales).
    3. Ignora códigos numéricos; busca por FUNCIÓN técnica.
    
    Responde estrictamente en JSON:
    {{
        "comp": "Nombre del competidor",
        "tienda": "Tienda en Uruguay",
        "imp": "Marca o Importador local",
        "precio": 0.0,
        "moneda": "USD/UYU",
        "um": "Presentación",
        "link": "URL del hallazgo en Uruguay",
        "rank": "Opiniones",
        "vs": "Diferencia técnica clave",
        "obs": "Notas (Promos/Stock)"
    }}
    """

    # --- INTENTO 1: GEMINI (GRATUITO Y PRIORITARIO) ---
    if "GOOGLE_API_KEY" in st.secrets:
        try:
            genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            # Limpieza de markdown
            res_text = response.text.replace('```json', '').replace('```', '').strip()
            return json.loads(res_text)
        except Exception as e:
            st.error(f"Error con Gemini: {e}")

    # --- INTENTO 2: OPENAI (SOLO SI TIENE SALDO) ---
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
            
    return None

def procesar_lote_industrial(df):
    resultados = []
    progreso = st.progress(0)
    # Detectar columnas
    col_desc = next((c for c in ['DESCRIPCION CORTA', 'Descripción', 'Especificación'] if c in df.columns), df.columns[0])
    col_url = next((c for c in ['URL', 'Enlace', 'Link', 'URL (Opcional pero recomendada)'] if c in df.columns), None)

    for index, row in df.iterrows():
        progreso.progress((index + 1) / len(df))
        if pd.notna(row[col_desc]):
            datos = ejecutar_analisis_ia(row[col_desc], row[col_url] if col_url else None)
            if datos:
                resultados.append({
                    "Descripción": row[col_desc],
                    "Competidor": datos['comp'],
                    "Tienda": datos['tienda'],
                    "Importador": datos['imp'],
                    "Precio": datos['precio'],
                    "Moneda": datos['moneda'],
                    "U.M": datos['um'],
                    "Link": datos['link'],
                    "Análisis": datos['vs']
                })
    return resultados
