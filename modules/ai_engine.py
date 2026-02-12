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

    PROTOCOLOS DE ANÁLISIS:
    1. DETECTIVE DE URL: Analiza el contenido de la URL. Si hay enlaces a Fichas Técnicas (PDF) o especificaciones, asume su contenido (composición química, torque, resistencia, normas ISO).
    2. DESESTIMACIÓN: Ignora cualquier código numérico. Céntrate en la FUNCIÓN del objeto.
    3. RASTREO URUGUAY: Busca competidores directos en Uruguay (Mercado Libre UY, Sodimac, Ferreterías Industriales). Identifica marcas como Sika, Fischer, 3M, Loctite, Stanley, etc.

    Responde en JSON:
    {{
        "comp": "Nombre exacto del competidor",
        "tienda": "Tienda en Uruguay",
        "imp": "Importador o Marca local",
        "precio": 0.0,
        "moneda": "USD/UYU",
        "um": "Presentación (ej. 310ml, Pack x100)",
        "link": "URL del producto en Uruguay",
        "rank": "Opiniones/Ranking detectado",
        "vs": "Diferencia técnica clave detectada",
        "obs": "Promos o info de stock"
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
    
    col_desc = next((c for c in ['DESCRIPCION CORTA', 'Descripción', 'Especificación'] if c in df.columns), df.columns[1])
    col_url = next((c for c in ['URL', 'Enlace', 'Link'] if c in df.columns), None)

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
