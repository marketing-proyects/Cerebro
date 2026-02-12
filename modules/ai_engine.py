import google.generativeai as genai
import openai
import streamlit as st
import json
import pandas as pd

def ejecutar_analisis_ia(descripcion, url_ref=None):
    prompt = f"""
    Objetivo: Investigador experto de Mercados para la competencia de los articulos subidos mediante excel. 
    Misión: encontrar competencia local en Uruguay basada en ADN técnico.

    PRODUCTO: {descripcion}
    URL REFERENCIA: {url_ref}

    INSTRUCCIONES:
    1. Analiza la URL para entender la química o mecánica. 
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

    if "GOOGLE_API_KEY" in st.secrets:
        try:
            genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
            model = genai.GenerativeModel('gemini-1.5-pro')
            response = model.generate_content(prompt)
            res_text = response.text.replace('```json', '').replace('```', '').strip()
            return json.loads(res_text)
        except:
            pass

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
    status_text = st.empty()
    progreso = st.progress(0)
    
    col_desc = next((c for c in ['DESCRIPCION CORTA', 'Descripción', 'Especificación'] if c in df.columns), df.columns[0])
    col_url = next((c for c in ['URL', 'Enlace', 'Link', 'URL (Opcional pero recomendada)'] if c in df.columns), None)

    total = len(df)
    for index, row in df.iterrows():
        pct = (index + 1) / total
        progreso.progress(pct)
        
        nombre_prod = str(row[col_desc])[:35] if pd.notna(row[col_desc]) else "Producto"
        status_text.text(f"Analizando {index + 1} de {total}: {nombre_prod}...")
        
        if pd.notna(row[col_desc]):
            url_val = row[col_url] if col_url else None
            datos = ejecutar_analisis_ia(row[col_desc], url_val)
            if datos:
                resultados.append({
                    "Descripción Original": row[col_desc],
                    "Producto Competidor": datos.get('comp', 'N/A'),
                    "Tienda (Venta)": datos.get('tienda', 'N/A'),
                    "Importador/Marca": datos.get('imp', 'N/A'),
                    "Precio": datos.get('precio', 0),
                    "Moneda": datos.get('moneda', 'N/A'),
                    "Presentación": datos.get('um', 'N/A'),
                    "Link Hallazgo": datos.get('link', 'N/A'),
                    "Análisis vs Würth": datos.get('vs', 'N/A')
                })
    status_text.empty()
    return resultados
