import google.generativeai as genai
import openai
import streamlit as st
import json
import pandas as pd
import re

def ejecutar_analisis_ia(descripcion, url_ref=None):
    # LIMPIEZA: Quitamos códigos de Würth para que no "ensucien" la búsqueda en Google UY
    desc_limpia = re.sub(r'\d{5,}', '', str(descripcion)).strip()
    
    prompt = f"""
    ERES UN INVESTIGADOR DE MERCADO TÉCNICO EN URUGUAY.
    
    PRODUCTO OBJETIVO: "{desc_limpia}"
    URL DE REFERENCIA (ESPECIFICACIONES): {url_ref}

    METODOLOGÍA OBLIGATORIA:
    1. IDENTIFICACIÓN TÉCNICA: Analiza la descripción y la URL. Determina qué es el producto (ej. Adhesivo MS, Disco de corte 115mm, Guante nitrilo). Usa la URL solo para entender la calidad y normas.
    
    2. BÚSQUEDA AGRESIVA EN URUGUAY: Busca en Google Uruguay, Mercado Libre Uruguay, Sodimac, Ingco, Salvador Livio, Pampín y otros proveedores locales.
    
    3. SELECCIÓN DE COMPETIDOR: Debes encontrar un reemplazo directo de OTRA MARCA (Sika, Fischer, 3M, Stanley, etc.) disponible actualmente en Uruguay.
    
    4. EXTRACCIÓN DE DATOS: Necesito el precio real, la tienda y el link.

    RESPONDE EXCLUSIVAMENTE EN ESTE FORMATO JSON:
    {{
        "comp": "Marca y modelo del competidor",
        "tienda": "Comercio en Uruguay",
        "imp": "Importador local",
        "precio": 0.0,
        "moneda": "USD/UYU",
        "um": "Presentación (ej. 310ml)",
        "link": "URL del hallazgo en Uruguay",
        "vs": "Análisis de por qué es el reemplazo ideal"
    }}
    """

    # --- MOTOR PRINCIPAL: GEMINI 1.5 PRO ---
    if "GOOGLE_API_KEY" in st.secrets:
        try:
            genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
            # Usamos el modelo Pro que tiene mejores capacidades de búsqueda y razonamiento
            model = genai.GenerativeModel('gemini-1.5-pro')
            
            # Forzamos la generación con una configuración que evite respuestas vacías
            response = model.generate_content(prompt)
            
            # Limpieza del resultado para asegurar JSON puro
            res_text = response.text.strip()
            if "```json" in res_text:
                res_text = res_text.split("```json")[1].split("```")[0].strip()
            elif "```" in res_text:
                res_text = res_text.split("```")[1].split("```")[0].strip()
                
            return json.loads(res_text)
        except Exception as e:
            # Si Gemini falla, intentamos con OpenAI de respaldo
            pass

    # --- MOTOR DE RESPALDO: OPENAI ---
    if "OPENAI_API_KEY" in st.secrets:
        try:
            client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
            response_oa = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                response_format={ "type": "json_object" }
            )
            return json.loads(response_oa.choices[0].message.content)
        except:
            pass

    # FALLBACK: Si ambos fallan, devolvemos una fila que indique el error técnico
    return {
        "comp": "Error de investigación",
        "tienda": "N/A",
        "imp": "N/A",
        "precio": 0,
        "moneda": "N/A",
        "um": "N/A",
        "link": "N/A",
        "vs": "No se pudo conectar con los motores de búsqueda."
    }

def procesar_lote_industrial(df):
    resultados = []
    status_text = st.empty()
    progreso = st.progress(0)
    
    # Identificación de columnas flexible
    col_desc = next((c for c in ['DESCRIPCION CORTA', 'Descripción'] if c in df.columns), df.columns[0])
    col_url = next((c for c in ['URL (Opcional pero recomendada)', 'URL', 'Link'] if c in df.columns), None)

    total = len(df)
    for index, row in df.iterrows():
        pct = (index + 1) / total
        progreso.progress(pct)
        
        desc_actual = str(row[col_desc])
        if pd.notna(row[col_desc]) and desc_actual.lower() != 'none':
            status_text.text(f"🕵️ Investigando {index + 1} de {total}: {desc_actual[:35]}...")
            
            url_val = row[col_url] if col_url and pd.notna(row[col_url]) else None
            datos = ejecutar_analisis_ia(desc_actual, url_val)
            
            resultados.append({
                "Descripción Original": desc_actual,
                "Producto Competidor": datos.get('comp'),
                "Tienda": datos.get('tienda'),
                "Precio": datos.get('precio'),
                "Moneda": datos.get('moneda'),
                "Presentación": datos.get('um'),
                "Link Hallazgo": datos.get('link'),
                "Análisis Estratégico": datos.get('vs')
            })
    
    status_text.empty()
    progreso.empty()
    return resultados
