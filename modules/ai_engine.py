import openai
import streamlit as st
import json
import pandas as pd

def ejecutar_analisis_ia(sku, descripcion, url_ref=None):
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    
    prompt = f"""
    Eres un Analista de Inteligencia de Mercado en Uruguay. 
    Tu misión es realizar un análisis competitivo profundo para este producto:
    
    PRODUCTO REFERENCIA:
    - Descripción: {descripcion}
    - URL de ADN Técnico: {url_ref}
    
    INSTRUCCIONES DE INVESTIGACIÓN:
    1. ANALIZA LA URL: Extrae la ficha técnica. Identifica qué es el producto (ej. Adhesivo MS, Silicona Neutra, Limpiador solvente), para qué sirve y sus especificaciones clave.
    2. RASTREO EN URUGUAY: Busca en tiempo real productos que compitan DIRECTAMENTE en Uruguay (Mercado Libre UY, Sodimac, ferreterías industriales locales).
    3. DETALLES DE COMPETENCIA: Encuentra marcas como Sika, Soudal, Fischer, 3M, Loctite o similares presentes en el mercado local.
    
    IMPORTANTE: Si no hay match exacto, busca el equivalente de mayor ranking.
    
    Responde estrictamente en JSON:
    {{
        "comp": "Nombre exacto del producto competencia",
        "tienda": "Comercio donde se vende en Uruguay",
        "imp": "Marca / Empresa que lo importa o fabrica",
        "precio": 0.0,
        "moneda": "USD o UYU",
        "um": "Presentación (ej. Cartucho 310ml, Spray 500ml)",
        "link": "URL del producto en el mercado uruguayo",
        "rank": "Puntaje/Ranking y volumen de comentarios detectado",
        "vs": "Comparativa de calidad: Würth vs Competencia",
        "obs": "Notas de interés (Promociones, stock, acciones detectadas)"
    }}
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o", 
            messages=[{"role": "user", "content": prompt}],
            response_format={ "type": "json_object" },
            temperature=0.2 # Menor temperatura para mayor precisión técnica
        )
        data = json.loads(response.choices[0].message.content)
        data['sku_orig'] = sku
        data['desc_orig'] = descripcion
        return data
    except:
        return None

def procesar_lote_industrial(df):
    resultados = []
    progreso = st.progress(0)
    
    # Identificación robusta de columnas
    col_sku = next((c for c in ['CODIGO', 'Material', 'Código'] if c in df.columns), df.columns[0])
    col_desc = next((c for c in ['DESCRIPCION CORTA', 'Descripción', 'Especificación'] if c in df.columns), df.columns[1])
    col_url = next((c for c in ['URL (Opcional pero recomendada)', 'URL', 'Enlace'] if c in df.columns), None)

    for index, row in df.iterrows():
        progreso.progress((index + 1) / len(df))
        if pd.notna(row[col_desc]):
            url = row[col_url] if col_url else None
            datos = ejecutar_analisis_ia(row[col_sku], row[col_desc], url)
            if datos:
                resultados.append({
                    "SKU Würth": datos['sku_orig'],
                    "Producto Competidor": datos['comp'],
                    "Tienda (Venta)": datos['tienda'],
                    "Importador/Marca": datos['imp'],
                    "Precio": datos['precio'],
                    "Moneda": datos['moneda'],
                    "Presentación": datos['um'],
                    "Link Referencia": datos['link'],
                    "Social Proof": datos['rank'],
                    "Würth vs Comp.": datos['vs'],
                    "Observaciones": datos['obs']
                })
    return resultados
