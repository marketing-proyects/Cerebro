import openai
import streamlit as st
import json
import pandas as pd

def ejecutar_analisis_ia(sku, descripcion, url_referencia=None):
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    
    contexto_producto = f"Descripción: {descripcion}"
    if url_referencia and str(url_referencia) != 'nan':
        contexto_producto += f" | URL de referencia: {url_referencia}"

    prompt = f"""
    Eres un analista senior de mercado en Uruguay. 
    Analiza el producto: {contexto_producto} (SKU: {sku})
    
    TAREA:
    Busca competidores directos en Uruguay (Mercado Libre, Sodimac, Ferreterías Industriales, Tiendas Especializadas).
    Si no encuentras información exacta, responde todos los campos de texto con "Info no encontrada" y los numéricos con 0.

    Responde estrictamente en JSON con este esquema:
    {{
        "competidor_producto": "Nombre exacto del producto competencia",
        "tienda_vendedora": "Nombre del comercio que lo vende",
        "importador_marca": "Empresa que lo importa o marca fabricante",
        "precio_valor": 0.0,
        "moneda": "USD/UYU",
        "unidad_medida": "ej: 500ml, 1kg, Pack x12",
        "enlace_referencia": "URL del hallazgo",
        "ranking_social": "Puntaje/Estrellas y cantidad de comentarios",
        "analisis_posicionamiento": "Nota de calidad percibida Würth vs Competencia",
        "comentarios_temporales": "Promociones, liquidaciones o eventos detectados"
    }}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={ "type": "json_object" },
            temperature=0.2
        )
        data = json.loads(response.choices[0].message.content)
        data['sku_original'] = sku
        data['desc_original'] = descripcion
        return data
    except:
        return None

def procesar_lote_industrial(df):
    resultados = []
    progreso = st.progress(0)
    
    # Identificación de columnas del Excel
    col_sku = next((c for c in ['Material', 'Nombre', 'Código'] if c in df.columns), df.columns[0])
    col_desc = next((c for c in ['Descripción', 'Especificación', 'Texto breve'] if c in df.columns), df.columns[1])
    col_url = next((c for c in ['URL', 'Enlace', 'Link'] if c in df.columns), None)

    for index, row in df.iterrows():
        progreso.progress((index + 1) / len(df))
        
        url_val = row[col_url] if col_url else None
        datos = ejecutar_analisis_ia(row[col_sku], row[col_desc], url_val)
        
        if datos:
            # Construimos la fila con las nuevas columnas separadas
            resultados.append({
                "SKU Würth": datos['sku_original'],
                "Descripción Würth": datos['desc_original'],
                "Producto Competidor": datos['competidor_producto'],
                "Tienda (Venta)": datos['tienda_vendedora'],
                "Importador/Marca": datos['importador_marca'],
                "Precio": datos['precio_valor'],
                "Moneda": datos['moneda'],
                "Presentación/U.M": datos['unidad_medida'],
                "Link Referencia": datos['enlace_referencia'],
                "Social Proof": datos['ranking_social'],
                "Würth vs Comp.": datos['analisis_posicionamiento'],
                "Observaciones Temporales": datos['comentarios_temporales']
            })
        else:
            # Fila de respaldo en caso de error crítico de la API
            resultados.append({
                "SKU Würth": row[col_sku],
                "Descripción Würth": row[col_desc],
                "Producto Competidor": "Error en proceso",
                "Tienda (Venta)": "Info no encontrada",
                "Importador/Marca": "Info no encontrada",
                "Precio": 0,
                "Moneda": "-",
                "Presentación/U.M": "-",
                "Link Referencia": "-",
                "Social Proof": "-",
                "Würth vs Comp.": "-",
                "Observaciones Temporales": "-"
            })
            
    return resultados
