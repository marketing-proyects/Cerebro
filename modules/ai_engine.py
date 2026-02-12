import openai
import streamlit as st
import json
import pandas as pd

def ejecutar_analisis_ia(descripcion, url_ref=None):
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    
    prompt = f"""
    Eres un Investigador Forense de Mercado Industrial en Uruguay. 
    Tu misión es desglosar la "Identidad Técnica" de un producto y encontrar su competencia local.

    ENTRADA DE DATOS:
    - Descripción: {descripcion}
    - URL Fuente: {url_ref}

    PROTOCOLOS DE INVESTIGACIÓN:
    1. ANALIZADOR DE URL: Analiza profundamente el contenido de la URL. Si detectas enlaces a Fichas Técnicas o PDFs, procesa su contenido implícito (composición, torque, resistencia, normas ISO).
    2. DESESTIMACIÓN TOTAL: Ignora códigos numéricos como "{descripcion.split(',')[0] if ',' in descripcion else ''}". Enfócate en la FUNCIÓN técnica.
    3. RASTREO URUGUAY: Busca competidores que cumplan la misma función en Mercado Libre UY, Sodimac Uruguay y ferreterías industriales locales. 
    4. MARCAS OBJETIVO: Sika, Fischer, 3M, Loctite, Stanley, etc. presentes en Uruguay.

    Responde estrictamente en JSON:
    {{
        "comp": "Nombre exacto del competidor",
        "tienda": "Comercio en Uruguay",
        "imp": "Marca / Importador local",
        "precio": 0.0,
        "moneda": "USD/UYU",
        "um": "Presentación (ej. 310ml, Pack x100)",
        "link": "URL del hallazgo en Uruguay",
        "rank": "Opiniones y ranking detectado",
        "vs": "Análisis técnico: Würth vs Competencia",
        "obs": "Acciones detectadas (Promos, stock, temporalidad)"
    }}
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o", 
            messages=[{"role": "user", "content": prompt}],
            response_format={ "type": "json_object" },
            temperature=0.1
        )
        data = json.loads(response.choices[0].message.content)
        return data
    except:
        return None

def procesar_lote_industrial(df):
    resultados = []
    progreso = st.progress(0)
    
    # Mapeo flexible de columnas para tu Excel
    col_desc = next((c for c in ['DESCRIPCION CORTA', 'Descripción', 'Especificación'] if c in df.columns), df.columns[0])
    col_url = next((c for c in ['URL', 'Enlace', 'Link', 'URL (Opcional pero recomendada)'] if c in df.columns), None)

    for index, row in df.iterrows():
        progreso.progress((index + 1) / len(df))
        if pd.notna(row[col_desc]):
            url = row[col_url] if col_url else None
            datos = ejecutar_analisis_ia(row[col_desc], url)
            if datos:
                resultados.append({
                    "Descripción Original": row[col_desc],
                    "Producto Competidor": datos['comp'],
                    "Tienda (Venta)": datos['tienda'],
                    "Importador/Marca": datos['imp'],
                    "Precio": datos['precio'],
                    "Moneda": datos['moneda'],
                    "Presentación": datos['um'],
                    "Link Referencia": datos['link'],
                    "Social Proof": datos['rank'],
                    "Análisis vs Würth": datos['vs'],
                    "Observaciones": datos['obs']
                })
    return resultados
