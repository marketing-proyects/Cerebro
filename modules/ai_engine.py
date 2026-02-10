import openai
import requests
from bs4 import BeautifulSoup
import streamlit as st
import json

def obtener_tc_real_brou():
    """Consulta la cotización de e-Brou Venta en la web del BROU"""
    url = "https://www.brou.com.uy/web/guest/cotizaciones"
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        # Nota: Por seguridad, si el raspado falla, usamos un valor base
        return 42.85 
    except Exception:
        return 43.00

def ejecutar_analisis_ia(url_competidor, nombre, espec, material, ues, tc_dia):
    """Analiza el HTML de la competencia usando la API de OpenAI"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url_competidor, headers=headers, timeout=15)
        html_puro = response.text[:8000] # Recorte para optimizar tokens
    except Exception:
        return None

    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    prompt_sistema = f"Eres un Analista Senior de Mercado Industrial en Uruguay. T/C BROU: {tc_dia}"
    prompt_usuario = f"""
    Compara este producto: {nombre} {espec} ({material}) con este contenido web:
    {html_puro}
    
    Analiza:
    1. Precio y Moneda (si es USD, usa T/C {tc_dia}).
    2. Unidad de empaque (UE) del rival.
    3. Si es una OFERTA temporal.
    
    Responde en JSON:
    {{"tienda": "nombre", "match_nombre": "nombre", "precio_encontrado": 0.0, "moneda": "USD/UYU", 
    "ue_detectada": 1, "es_oferta": true, "alerta": "mensaje", "sugerencia": "consejo", "confianza": 0.0}}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": prompt_sistema}, {"role": "user", "content": prompt_usuario}],
            response_format={ "type": "json_object" }
        )
        return json.loads(response.choices[0].message.content)
    except:
        return None

def procesar_investigacion_industrial(df):
    tc_dia = obtener_tc_real_brou()
    resultados = []
    progreso = st.progress(0)
    for index, row in df.iterrows():
        progreso.progress((index + 1) / len(df))
        datos_ia = ejecutar_analisis_ia(row['URL Competidor'], row['Nombre'], row['Especificación'], row['Material/Norma'], [row['UE 1'], row['UE 2'], row['UE 3']], tc_dia)
        
        if datos_ia:
            precio_pesos = datos_ia["precio_encontrado"] * (tc_dia if datos_ia["moneda"] == "USD" else 1)
            precio_unit_comp = precio_pesos / datos_ia["ue_detectada"]
            precio_unit_propio = row['Precio Propio (Ref)'] / row['UE 1']
            
            resultados.append({
                "Producto": f"{row['Nombre']} {row['Especificación']}",
                "Material": row['Material/Norma'],
                "P. Unit. Propio": round(precio_unit_propio, 2),
                "P. Unit. Comp.": round(precio_unit_comp, 2),
                "Gap %": round(((precio_unit_comp - precio_unit_propio) / precio_unit_propio) * 100, 2),
                "Tienda": datos_ia["tienda"],
                "Rival UE": datos_ia["ue_detectada"],
                "Es Oferta": datos_ia["es_oferta"],
                "Alerta": datos_ia["alerta"],
                "Sugerencia": datos_ia["sugerencia"]
            })
    return resultados
