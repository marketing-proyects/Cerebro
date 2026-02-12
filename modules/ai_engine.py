import openai
import google.generativeai as genai
import streamlit as st
import json
import pandas as pd

def ejecutar_analisis_ia(descripcion, url_ref=None):
    # 1. Configuración de Modelos
    # Gemini (Google)
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model_gemini = genai.GenerativeModel('gemini-1.5-pro')
    
    # OpenAI / Copilot Engine (GPT-4o)
    client_oa = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    prompt = f"""
    Eres un Investigador Forense de Mercados para Würth Uruguay. 
    Tu misión es encontrar competencia local basada en ADN técnico.

    PRODUCTO: {descripcion}
    URL REFERENCIA: {url_ref}

    INSTRUCCIONES:
    1. Analiza la URL para entender la química/mecánica del producto (aunque sea de España).
    2. Busca equivalentes en Uruguay (Mercado Libre UY, Sodimac, Ferreterías Industriales).
    3. Identifica marcas competidoras: Sika, Fischer, 3M, Loctite, Stanley, etc.
    
    Responde estrictamente en JSON:
    {{
        "comp": "Nombre del competidor",
        "tienda": "Tienda en Uruguay",
        "imp": "Marca o Importador local",
        "precio": 0.0,
        "moneda": "USD/UYU",
        "um": "Presentación (ej. 310ml)",
        "link": "URL del hallazgo en Uruguay",
        "rank": "Social Proof / Opiniones",
        "vs": "Diferencia técnica clave",
        "obs": "Acciones detectadas (Promos/Stock)"
    }}
    """

    # --- ESTRATEGIA DE TRIANGULACIÓN ---
    
    # Intento 1: Gemini (Mejor para búsqueda web en Uruguay)
    try:
        response = model_gemini.generate_content(prompt)
        json_clean = response.text.replace('```json', '').replace('```', '').strip()
        data = json.loads(json_clean)
        if data.get("precio", 0) > 0:
            data["motor_utilizado"] = "Gemini (Google)"
            return data
    except:
        pass

    # Intento 2: OpenAI / Copilot (Mejor para razonamiento técnico y equivalencias)
    try:
        response_oa = client_oa.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={ "type": "json_object" }
        )
        data = json.loads(response_oa.choices[0].message.content)
        data["motor_utilizado"] = "GPT-4o (Copilot Engine)"
        return data
    except:
        return None

def procesar_lote_industrial(df):
    resultados = []
    progreso = st.progress(0)
    
    col_desc = next((c for c in ['DESCRIPCION CORTA', 'Descripción', 'Especificación'] if c in df.columns), df.columns[0])
    col_url = next((c for c in ['URL', 'Enlace', 'Link', 'URL (Opcional pero recomendada)'] if c in df.columns), None)

    for index, row in df.iterrows():
        progreso.progress((index + 1) / len(df))
        if pd.notna(row[col_desc]):
            url = row[col_url] if col_url else None
            datos = ejecutar_analisis_ia(row[col_desc], url)
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
                    "Análisis": datos['vs'],
                    "Motor": datos.get('motor_utilizado', 'N/A')
                })
    return resultados
