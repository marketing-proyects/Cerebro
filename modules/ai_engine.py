import google.generativeai as genai
import openai
import streamlit as st
import json
import pandas as pd
import re

def ejecutar_analisis_ia(descripcion, url_ref=None):
    # 1. LIMPIEZA RADICAL: Eliminamos cualquier código numérico de más de 4 dígitos.
    # Esto evita que la IA se pierda buscando códigos internos de Würth.
    desc_para_ia = re.sub(r'\d{5,}', '', str(descripcion)).strip()
    
    # 2. PROMPT DE INVESTIGACIÓN AGRESIVA
    prompt = f"""
    Eres un Investigador Forense de Mercados para el sector industrial en URUGUAY. 
    Tu misión es encontrar un producto COMPETIDOR local para: "{desc_para_ia}".

    DATOS DISPONIBLES:
    - ADN del producto: {desc_para_ia}
    - Referencia técnica (URL): {url_ref}

    PROTOCOLOS DE BÚSQUEDA:
    1. PRIORIDAD SEMÁNTICA: Si la descripción menciona "Adhesivo MS", "Silicona", "Disco de Corte" o "Frenos", busca por esa función técnica.
    2. LOCALIZACIÓN URUGUAY: Busca precios reales en Mercado Libre Uruguay (mercadolibre.com.uy), Sodimac Uruguay o ferreterías industriales locales.
    3. COMPETIDORES CLAVE: Busca marcas equivalentes presentes en Uruguay: Sika, Fischer, 3M, Loctite, Stanley, Bosch, Thompson.
    4. PROHIBIDO RENDIRSE: No acepto "No encontrado". Si no hay un link exacto, provee el link de la marca competidora líder en Uruguay que cumpla la misma función.
    
    Responde estrictamente en este formato JSON:
    {{
        "comp": "Marca y modelo competidor detectado en Uruguay",
        "tienda": "Nombre del comercio (ej. Sodimac, ML, Ferretería X)",
        "imp": "Marca o Importador",
        "precio": 0.0,
        "moneda": "USD o UYU",
        "um": "Presentación (ej. 310ml, Pack x100)",
        "link": "URL real del hallazgo en Uruguay",
        "vs": "Breve comparativa técnica entre Würth y el competidor"
    }}
    """

    # --- MOTOR PRIMARIO: GEMINI 1.5 PRO (Búsqueda en Uruguay) ---
    if "GOOGLE_API_KEY" in st.secrets:
        try:
            genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
            model = genai.GenerativeModel('gemini-1.5-pro')
            response = model.generate_content(prompt)
            res_text = response.text.replace('```json', '').replace('```', '').strip()
            return json.loads(res_text)
        except:
            pass

    # --- MOTOR DE RESPALDO: OPENAI (GPT-4o) ---
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
    
    # FALLBACK: Si no hay conexión, devolvemos un estado informativo
    return {
        "comp": "Error de conexión IA", "tienda": "N/A", "imp": "N/A", 
        "precio": 0, "moneda": "N/A", "um": "N/A", "link": "N/A", 
        "vs": f"Fallo al analizar {desc_para_ia}"
    }

def procesar_lote_industrial(df):
    resultados = []
    status_text = st.empty()
    progreso = st.progress(0)
    
    # Identificación flexible de columnas
    col_desc = next((c for c in ['DESCRIPCION CORTA', 'Descripción'] if c in df.columns), df.columns[0])
    col_url = next((c for c in ['URL (Opcional pero recomendada)', 'URL', 'Link'] if c in df.columns), None)

    total = len(df)
    for index, row in df.iterrows():
        pct = (index + 1) / total
        progreso.progress(pct)
        
        desc_actual = str(row[col_desc])
        if pd.notna(row[col_desc]) and desc_actual.lower() != 'none' and desc_actual.strip() != '':
            status_text.text(f"🕵️ Investigando {index + 1} de {total}: {desc_actual[:30]}...")
            
            url_val = row[col_url] if col_url and pd.notna(row[col_url]) else None
            datos = ejecutar_analisis_ia(desc_actual, url_val)
            
            resultados.append({
                "Descripción Original": desc_actual,
                "Producto Competidor": datos.get('comp'),
                "Tienda (Venta)": datos.get('tienda'),
                "Importador/Marca": datos.get('imp'),
                "Precio": datos.get('precio'),
                "Moneda": datos.get('moneda'),
                "Presentación": datos.get('um'),
                "Link Hallazgo": datos.get('link'),
                "Análisis vs Würth": datos.get('vs')
            })
    
    status_text.empty()
    progreso.empty()
    return resultados
