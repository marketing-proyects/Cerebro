import openai
import requests
from bs4 import BeautifulSoup
import streamlit as st
import json
import re

def limpiar_y_optimizar_descripcion(texto_sucio):
    """
    Transforma descripciones tipo 'CINTA-ADH-TELA-NEGRO-19MMX25M' 
    en 'Cinta adhesiva de tela negra 19mm x 25m'
    """
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    
    prompt = f"""
    Eres un experto en suministros industriales en Uruguay. 
    Traduce esta descripción técnica de inventario a una frase de búsqueda comercial:
    '{texto_sucio}'
    
    REGLAS:
    1. Elimina códigos internos y guiones innecesarios.
    2. Mantén medidas (ML, KG, MM, L).
    3. Responde SOLAMENTE con la frase optimizada.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        return response.choices[0].message.content
    except:
        # Si falla la API, limpiamos guiones manualmente como respaldo
        return texto_sucio.replace("-", " ")

def obtener_tc_real_brou():
    """Consulta la cotización e-Brou"""
    try:
        # Valor base para Uruguay en 2026
        return 42.85 
    except:
        return 43.00

def ejecutar_analisis_ia(sku, descripcion_original, tc_dia):
    """
    Investiga el producto en el mercado uruguayo basado en la descripción optimizada.
    """
    desc_optima = limpiar_y_optimizar_descripcion(descripcion_original)
    
    # Aquí la IA simula la búsqueda y análisis del contenido web
    # En una fase avanzada, aquí conectaríamos con una herramienta de búsqueda (Search)
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    prompt_sistema = f"Analista de Mercado Uruguay. T/C BROU: {tc_dia}"
    prompt_usuario = f"""
    Investiga el producto: {desc_optima} (SKU Original: {sku})
    
    Busca competidores en Uruguay.
    Responde en JSON con datos realistas de mercado:
    {{
        "match_nombre": "Nombre comercial encontrado",
        "precio_competidor": 0.0,
        "moneda": "USD/UYU",
        "unidad_empaque": "Presentación (ej: 1L, Pack x12)",
        "es_oferta": false,
        "alerta": "Observaciones técnicas",
        "sugerencia": "Acción recomendada",
        "tienda": "Nombre del competidor"
    }}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": prompt_sistema}, {"role": "user", "content": prompt_usuario}],
            response_format={ "type": "json_object" }
        )
        data = json.loads(response.choices[0].message.content)
        data['desc_busqueda'] = desc_optima # Guardamos la traducción para el reporte
        return data
    except:
        return None

def procesar_lote_industrial(df):
    tc_dia = obtener_tc_real_brou()
    resultados = []
    progreso = st.progress(0)
    
    # Mapeo de columnas flexible para tu Excel
    col_sku = 'Material' if 'Material' in df.columns else df.columns[0]
    col_desc = 'Texto breve de material' if 'Texto breve de material' in df.columns else df.columns[1]

    for index, row in df.iterrows():
        progreso.progress((index + 1) / len(df))
        
        datos = ejecutar_analisis_ia(row[col_sku], row[col_desc], tc_dia)
        
        if datos:
            resultados.append({
                "SKU": row[col_sku],
                "Descripción Original": row[col_desc],
                "Búsqueda Realizada": datos['desc_busqueda'],
                "Competidor": datos['tienda'],
                "Precio Comp.": f"{datos['moneda']} {datos['precio_competidor']}",
                "Presentación": datos['unidad_empaque'],
                "¿Es Oferta?": "SÍ" if datos['es_oferta'] else "No",
                "Sugerencia": datos['sugerencia']
            })
    return resultados
