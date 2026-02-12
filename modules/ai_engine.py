import streamlit as st
import json
import re
import time
import google.generativeai as genai
from groq import Groq
import requests

def ejecutar_analisis_ia(descripcion, url_ref=None):
    desc_limpia = re.sub(r'\d{5,}', '', str(descripcion)).strip()
    
    prompt = f"""
    Eres un Investigador Senior de Compras Industriales en Uruguay.
    Misión: Encontrar un reemplazo de OTRA MARCA para: "{desc_limpia}" en Uruguay.
    Referencia: {url_ref}

    METODOLOGÍA:
    1. Identifica el producto.
    2. Busca en: mercadolibre.com.uy, sodimac.com.uy, ingco.com.uy, salvadorlivio.com.uy, pampin.com.uy.
    3. Dame el precio real y link de Uruguay.

    Responde ESTRICTAMENTE en JSON:
    {{
        "comp": "Marca y modelo",
        "tienda": "Tienda en Uruguay",
        "precio": 0.0,
        "moneda": "USD/UYU",
        "link": "URL exacta",
        "vs": "Análisis"
    }}
    """

    # --- 1. MOTOR PRINCIPAL: GROQ (Ultra Rápido) ---
    if "GROQ_API_KEY" in st.secrets:
        try:
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            return json.loads(completion.choices[0].message.content)
        except Exception as e:
            st.warning(f"Groq en espera... reintentando")

    # --- 2. RESPALDO: HUGGING FACE (Mistral) ---
    if "HF_TOKEN" in st.secrets:
        try:
            API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3"
            headers = {"Authorization": f"Bearer {st.secrets['HF_TOKEN']}"}
            response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
            res_text = response.json()[0]['generated_text']
            # Extraer JSON del texto
            json_match = re.search(r'\{.*\}', res_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except: pass

    # --- 3. BACKUP FINAL: GEMINI (Tu cuenta personal) ---
    if "GOOGLE_API_KEY" in st.secrets:
        try:
            genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            res_text = response.text
            json_match = re.search(r'\{.*\}', res_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except: pass

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
        status_text.info(f"🕵️ Investigando {index+1}/{total}: {desc_actual[:30]}")
        
        url_val = row[col_url] if col_url and pd.notna(row[col_url]) else None
        datos = ejecutar_analisis_ia(desc_actual, url_val)
        
        if datos:
            resultados.append({
                "Descripción Original": desc_actual,
                "Producto Competidor": datos.get('comp'),
                "Tienda": datos.get('tienda'),
                "Precio": datos.get('precio'),
                "Moneda": datos.get('moneda'),
                "Link Hallazgo": datos.get('link'),
                "Análisis": datos.get('vs')
            })
        else:
            resultados.append({
                "Descripción Original": desc_actual,
                "Producto Competidor": "Sin resultados", "Tienda": "N/A", "Precio": 0, "Moneda": "N/A", "Link Hallazgo": "N/A", "Análisis": "Error en motores"
            })
        time.sleep(1) # Pausa mínima para no saturar
            
    status_text.empty()
    progreso.empty()
    return resultados
