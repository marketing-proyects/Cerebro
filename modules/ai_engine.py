from genai import Client
import openai
import streamlit as st
import json
import pandas as pd
import re

def ejecutar_analisis_ia(descripcion, url_ref=None):
    # LIMPIEZA: Quitamos códigos de Würth para que la IA busque el concepto técnico
    desc_limpia = re.sub(r'\d{5,}', '', str(descripcion)).strip()
    
    # PROMPT DE INVESTIGACIÓN AGRESIVA
    prompt = f"""
    ERES UN INVESTIGADOR DE MERCADO INDUSTRIAL EN URUGUAY.
    
    PRODUCTO A ANALIZAR: "{desc_limpia}"
    URL DE REFERENCIA TÉCNICA: {url_ref}

    METODOLOGÍA OBLIGATORIA:
    1. IDENTIFICACIÓN TÉCNICA: Analiza la descripción y la URL. Identifica qué es el producto (ej. Adhesivo MS, Disco de corte, etc.). Ignora que la URL sea extranjera; úsala solo para extraer especificaciones técnicas.
    
    2. BÚSQUEDA REAL EN URUGUAY: Busca activamente en Google Uruguay, Mercado Libre Uruguay, Sodimac, Ingco, Salvador Livio, Pampín y otros proveedores locales.
    
    3. SELECCIÓN DE COMPETIDOR: Debes encontrar productos de OTRAS MARCAS (Sika, Fischer, 3M, Stanley, etc.) que se vendan en Uruguay y sean el reemplazo directo.
    
    4. RESPUESTA OBLIGATORIA: No acepto campos vacíos. Si no encuentras el link exacto, provee el link de la marca líder competidora en Uruguay.

    RESPONDE EXCLUSIVAMENTE EN JSON:
    {{
        "comp": "Marca y modelo competidor",
        "tienda": "Comercio en Uruguay",
        "imp": "Importador/Marca",
        "precio": 0.0,
        "moneda": "USD/UYU",
        "um": "Presentación",
        "link": "URL del hallazgo en Uruguay",
        "vs": "Análisis de reemplazo"
    }}
    """

    # --- NUEVA LIBRERÍA GOOGLE GENAI ---
    if "GOOGLE_API_KEY" in st.secrets:
        try:
            client_google = Client(api_key=st.secrets["GOOGLE_API_KEY"])
            # Usamos el modelo con capacidad de búsqueda (Search Tool)
            response = client_google.models.generate_content(
                model="gemini-2.0-flash", 
                contents=prompt
            )
            
            res_text = response.text
            # Limpiamos el JSON por si la IA pone basura alrededor
            if "```json" in res_text:
                res_text = res_text.split("```json")[1].split("```")[0].strip()
            return json.loads(res_text)
        except Exception as e:
            # Si falla Google, intentamos con OpenAI
            pass

    # --- RESPALDO: OPENAI ---
    if "OPENAI_API_KEY" in st.secrets:
        try:
            client_oa = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
            response_oa = client_oa.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                response_format={ "type": "json_object" }
            )
            return json.loads(response_oa.choices[0].message.content)
        except:
            pass

    return {
        "comp": "Error de investigación", "tienda": "N/A", "imp": "N/A", 
        "precio": 0, "moneda": "N/A", "um": "N/A", "link": "N/A", "vs": "Revisar conexión"
    }

def procesar_lote_industrial(df):
    resultados = []
    status_text = st.empty()
    progreso = st.progress(0)
    
    col_desc = next((c for c in ['DESCRIPCION CORTA', 'Descripción'] if c in df.columns), df.columns[0])
    col_url = next((c for c in ['URL (Opcional pero recomendada)', 'URL', 'Link'] if c in df.columns), None)

    total = len(df)
    for index, row in df.iterrows():
        pct = (index + 1) / total
        progreso.progress(pct)
        
        desc_actual = str(row[col_desc])
        if pd.notna(row[col_desc]) and desc_actual.lower() != 'none':
            status_text.text(f"🕵️ Investigando en Uruguay: {desc_actual[:35]}...")
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
                "Análisis de Reemplazo": datos.get('vs')
            })
    
    status_text.empty()
    progreso.empty()
    return resultados
