import google.generativeai as genai
import openai
import streamlit as st
import json
import pandas as pd
import re
import time

def ejecutar_analisis_ia(descripcion, url_ref=None):
    desc_limpia = re.sub(r'\d{5,}', '', str(descripcion)).strip()
    
    prompt = f"""
    Eres un experto en compras industriales en Uruguay. 
    Busca un COMPETIDOR local para: "{desc_limpia}"
    Usa esta referencia: {url_ref}

    METODOLOGÍA:
    1. Busca en dominios .com.uy (Sodimac, Mercado Libre UY, Ingco, etc.).
    2. Encuentra una marca distinta (Sika, 3M, Fischer, etc.).
    3. Dame el precio real y el link de la tienda en Uruguay.

    Responde ESTRICTAMENTE en JSON:
    {{
        "comp": "Marca y modelo",
        "tienda": "Tienda en Uruguay",
        "precio": 0.0,
        "moneda": "USD/UYU",
        "link": "URL exacta en Uruguay",
        "vs": "Diferencia técnica"
    }}
    """

    # --- INTENTO 1: GEMINI (Motor de búsqueda) ---
    if "GOOGLE_API_KEY" in st.secrets:
        try:
            genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
            model = genai.GenerativeModel('gemini-1.5-pro') # Usamos el Pro para mejor calidad
            response = model.generate_content(prompt)
            res_text = response.text
            if "{" in res_text:
                res_text = res_text[res_text.find("{"):res_text.rfind("}")+1]
                return json.loads(res_text)
        except:
            pass # Si falla, pasamos al siguiente motor silenciosamente

    # --- INTENTO 2: OPENAI GPT-4o (Motor de razonamiento de respaldo) ---
    if "OPENAI_API_KEY" in st.secrets:
        try:
            client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
            response_oa = client.chat.completions.create(
                model="gpt-4o", # Usamos la versión más potente
                messages=[{"role": "user", "content": prompt}],
                response_format={ "type": "json_object" }
            )
            return json.loads(response_oa.choices[0].message.content)
        except:
            pass

    return None

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
        status_text.text(f"🕵️ Multi-IA analizando: {desc_actual[:30]}...")
        
        url_val = row[col_url] if col_url and pd.notna(row[col_url]) else None
        
        # Ejecución Híbrida
        datos = ejecutar_analisis_ia(desc_actual, url_val)
        
        if datos:
            resultados.append({
                "Descripción Original": desc_actual,
                "Competidor": datos.get('comp'),
                "Tienda": datos.get('tienda'),
                "Precio": datos.get('precio'),
                "Moneda": datos.get('moneda'),
                "Link": datos.get('link'),
                "Análisis": datos.get('vs')
            })
        else:
            resultados.append({
                "Descripción Original": desc_actual,
                "Competidor": "No hallado por ninguna IA",
                "Tienda": "N/A", "Precio": 0, "Moneda": "N/A", "Link": "N/A", "Análisis": "N/A"
            })
        
        time.sleep(1) # Pequeña pausa para estabilidad
            
    status_text.empty()
    progreso.empty()
    return resultados
