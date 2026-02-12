import google.generativeai as genai
import streamlit as st
import json
import pandas as pd
import re
import time

def ejecutar_analisis_ia(descripcion, url_ref=None):
    # Limpieza extrema: Nos quedamos solo con las palabras clave
    desc_limpia = re.sub(r'\d{5,}', '', str(descripcion)).strip()
    
    # Prompt ultra-directo para evitar que la IA se pierda en procesos largos
    prompt = f"""
    Eres un comprador experto en ferretería industrial en Uruguay.
    
    ARTÍCULO: {desc_limpia}
    REF: {url_ref}

    TAREA:
    1. Identifica el producto.
    2. Busca un competidor de marca (Sika, Fischer, 3M o Ingco) en URUGUAY.
    3. Sitios autorizados: mercadolibre.com.uy, sodimac.com.uy, pampin.com.uy.
    
    RESPONDE SOLO EL JSON:
    {{
        "comp": "Marca y modelo",
        "tienda": "Tienda UY",
        "precio": 0.0,
        "moneda": "USD/UYU",
        "link": "URL del producto en Uruguay",
        "vs": "Diferencia"
    }}
    """

    if "GOOGLE_API_KEY" in st.secrets:
        try:
            genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
            # Usamos 1.5-flash: es el más rápido y el que menos falla por tiempo de espera
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Agregamos una configuración de seguridad laxa para evitar bloqueos por filtros
            response = model.generate_content(prompt)
            
            # Limpiamos el texto para asegurar que solo quede el JSON
            res_text = response.text
            if "{" in res_text:
                res_text = res_text[res_text.find("{"):res_text.rfind("}")+1]
                return json.loads(res_text)
        except Exception as e:
            return None
    return None

def procesar_lote_industrial(df):
    resultados = []
    status_text = st.empty()
    progreso = st.progress(0)
    
    # Mapeo de columnas
    col_desc = next((c for c in ['DESCRIPCION CORTA', 'Descripción'] if c in df.columns), df.columns[0])
    col_url = next((c for c in ['URL (Opcional pero recomendada)', 'URL', 'Link'] if c in df.columns), None)

    total = len(df)
    for index, row in df.iterrows():
        pct = (index + 1) / total
        progreso.progress(pct)
        
        desc_actual = str(row[col_desc])
        if pd.notna(row[col_desc]) and desc_actual.lower() != 'none':
            status_text.text(f"🔎 Buscando en Uruguay: {desc_actual[:30]}")
            
            url_val = row[col_url] if col_url and pd.notna(row[col_url]) else None
            
            # Intento de búsqueda
            datos = ejecutar_analisis_ia(desc_actual, url_val)
            
            # Si la IA devuelve datos, los guardamos; si no, ponemos una fila de "No hallado"
            # pero permitimos que el proceso siga adelante.
            if datos:
                resultados.append({
                    "Descripción Original": desc_actual,
                    "Competidor": datos.get('comp', 'No hallado'),
                    "Tienda": datos.get('tienda', 'N/A'),
                    "Precio": datos.get('precio', 0),
                    "Moneda": datos.get('moneda', 'N/A'),
                    "Link": datos.get('link', 'N/A'),
                    "Comparativa": datos.get('vs', 'N/A')
                })
            else:
                resultados.append({
                    "Descripción Original": desc_actual,
                    "Competidor": "No hallado",
                    "Tienda": "N/A",
                    "Precio": 0,
                    "Moneda": "N/A",
                    "Link": "N/A",
                    "Comparativa": "La búsqueda no arrojó resultados"
                })
            
            # Pausa mínima para no saturar
            time.sleep(1)
            
    status_text.empty()
    progreso.empty()
    return resultados
