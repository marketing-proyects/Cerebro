import google.generativeai as genai
import openai
import streamlit as st
import json
import pandas as pd
import re

def ejecutar_analisis_ia(descripcion, url_ref=None):
    # 1. LIMPIEZA DE DATOS: Eliminamos códigos numéricos largos que distraen a la IA
    # Esto quita SKUs como 893226101 para que la IA se enfoque en "Adhesivo MS"
    desc_limpia = re.sub(r'\d{5,}', '', descripcion).strip()
    
    prompt = f"""
    Eres un Analista Senior de Mercado para Würth Uruguay. 
    Tu misión es encontrar el precio y competidor de un producto basado en su ADN técnico.

    DATOS DE ENTRADA:
    - Descripción del Producto: {desc_limpia}
    - URL de ADN Técnico: {url_ref}

    PROTOCOLOS OBLIGATORIOS:
    1. ANALIZA LA URL: Si la URL es de España u otro país, DEBES entrar y extraer la función técnica (ej. es un sellador polímero MS, es un disco de corte para acero inox, es un guante de nitrilo).
    2. TRADUCCIÓN AL MERCADO LOCAL: Con esa base técnica, busca productos equivalentes en URUGUAY (Mercado Libre UY, Sodimac Uruguay, Ferreterías Industriales como Rumbo, herramientas.com.uy, etc.).
    3. COMPETENCIA DIRECTA: Busca marcas presentes en Uruguay: Sika, Fischer, 3M, Loctite, Stanley, Bosch, Thompson. 
    4. NO TE RINDAS: Está prohibido responder "No encontrado". Si no encuentras el link exacto, provee el del competidor más cercano en Uruguay.

    Responde estrictamente en este formato JSON:
    {{
        "comp": "Marca y modelo del competidor en Uruguay",
        "tienda": "Nombre del comercio uruguayo",
        "imp": "Importador o Marca local",
        "precio": 0.0,
        "moneda": "USD o UYU",
        "um": "Presentación (ej. 310ml)",
        "link": "URL del hallazgo en Uruguay",
        "vs": "Por qué este producto compite con el original",
        "obs": "Notas sobre promociones o stock"
    }}
    """

    # --- MOTOR PRIMARIO: GEMINI 1.5 PRO (Búsqueda Web Uruguay) ---
    if "GOOGLE_API_KEY" in st.secrets:
        try:
            genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
            model = genai.GenerativeModel('gemini-1.5-pro')
            response = model.generate_content(prompt)
            # Limpieza de posibles tags de markdown en la respuesta
            res_text = response.text.replace('```json', '').replace('```', '').strip()
            return json.loads(res_text)
        except Exception as e:
            # En caso de error, el sistema registrará el fallo silenciosamente y pasará al respaldo
            pass

    # --- MOTOR DE RESPALDO: OPENAI GPT-4o ---
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
    
    # --- FALLBACK DE SEGURIDAD (Si nada funciona, devolvemos estructura vacía para no romper el Excel) ---
    return {
        "comp": "Buscando...", 
        "tienda": "Pendiente", 
        "imp": "N/A", 
        "precio": 0, 
        "moneda": "N/A", 
        "um": "N/A", 
        "link": "N/A", 
        "vs": "Falla en conexión de IA",
        "obs": "Reintentar análisis"
    }

def procesar_lote_industrial(df):
    resultados = []
    status_text = st.empty()
    progreso = st.progress(0)
    
    # Mapeo flexible de columnas para el Excel del usuario
    col_desc = next((c for c in ['DESCRIPCION CORTA', 'Descripción', 'Especificación'] if c in df.columns), df.columns[0])
    col_url = next((c for c in ['URL', 'Enlace', 'Link', 'URL (Opcional pero recomendada)'] if c in df.columns), None)

    total = len(df)
    for index, row in df.iterrows():
        pct = (index + 1) / total
        progreso.progress(pct)
        
        nombre_prod = str(row[col_desc])[:35] if pd.notna(row[col_desc]) else "Procesando..."
        status_text.text(f"🕵️ Investigando {index + 1} de {total}: {nombre_prod}")
        
        if pd.notna(row[col_desc]):
            url_val = row[col_url] if col_url else None
            datos = ejecutar_analisis_ia(row[col_desc], url_val)
            
            if datos:
                resultados.append({
                    "Descripción Original": row[col_desc],
                    "Producto Competidor": datos.get('comp'),
                    "Tienda (Venta)": datos.get('tienda'),
                    "Importador/Marca": datos.get('imp'),
                    "Precio": datos.get('precio'),
                    "Moneda": datos.get('moneda'),
                    "Presentación": datos.get('um'),
                    "Link Hallazgo": datos.get('link'),
                    "Análisis vs Würth": datos.get('vs'),
                    "Observaciones": datos.get('obs')
                })
    
    status_text.empty()
    progreso.empty()
    return resultados
