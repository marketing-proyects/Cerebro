import openai
import streamlit as st
import json
import pandas as pd

def ejecutar_analisis_ia(sku, descripcion, url_ref=None):
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    
    prompt = f"""
    Eres un Investigador de Mercado Industrial en Uruguay. 
    Tu objetivo es encontrar competidores LOCALES para un producto de referencia.

    DATOS DE REFERENCIA (Würth):
    - Descripción corta: {descripcion}
    - SKU interno (solo referencia): {sku}
    - URL de referencia técnica: {url_ref}

    PASOS DE TU INVESTIGACIÓN:
    1. ANALIZA LA URL: Si hay una URL (aunque sea de España o Alemania), entra y extrae: composición técnica (ej. Polímero MS, Cianocrilato), uso (ej. pegado de espejos, limpieza de frenos) y beneficios.
    2. BUSCA EN URUGUAY: Con ese perfil técnico, busca productos equivalentes en: Mercado Libre Uruguay, Sodimac.com.uy, y ferreterías industriales uruguayas.
    3. IDENTIFICA: Marca del competidor, quién lo importa/fabrica y quién lo vende (tienda).

    REGLA: No busques el código {sku}. Busca productos que CUMPLAN LA MISMA FUNCIÓN técnica en Uruguay.

    Responde en JSON:
    {{
        "comp": "Nombre del producto competidor",
        "tienda": "Comercio donde se vende en Uruguay",
        "imp": "Marca o Importador detectado",
        "precio": 0.0,
        "moneda": "USD/UYU",
        "um": "Presentación (ml, gr, kg)",
        "link": "URL del producto en Uruguay",
        "rank": "Opiniones/Ranking",
        "vs": "Comparativa técnica rápida con Würth",
        "obs": "Notas, promos o info de stock"
    }}
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o", 
            messages=[{"role": "user", "content": prompt}],
            response_format={ "type": "json_object" },
            temperature=0.3
        )
        data = json.loads(response.choices[0].message.content)
        data['sku'] = sku
        data['desc'] = descripcion
        return data
    except:
        return None

def procesar_lote_industrial(df):
    resultados = []
    progreso = st.progress(0)
    
    # Mapeo de columnas
    col_sku = next((c for c in ['Material', 'CODIGO', 'Código'] if c in df.columns), df.columns[0])
    col_desc = next((c for c in ['Descripción', 'DESCRIPCION CORTA', 'Especificación'] if c in df.columns), df.columns[1])
    col_url = next((c for c in ['URL', 'Enlace', 'Link'] if c in df.columns), None)

    for index, row in df.iterrows():
        progreso.progress((index + 1) / len(df))
        if pd.notna(row[col_desc]):
            url = row[col_url] if col_url else None
            datos = ejecutar_analisis_ia(row[col_sku], row[col_desc], url)
            if datos:
                resultados.append({
                    "SKU Würth": datos['sku'],
                    "Producto Competidor": datos['comp'],
                    "Tienda (Venta)": datos['tienda'],
                    "Importador/Marca": datos['imp'],
                    "Precio Mercado": datos['precio'],
                    "Moneda": datos['moneda'],
                    "Presentación": datos['um'],
                    "Link": datos['link'],
                    "Würth vs Comp.": datos['vs'],
                    "Observaciones": datos['obs']
                })
    return resultados
