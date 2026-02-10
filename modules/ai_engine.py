import openai
import streamlit as st
import json
import pandas as pd

def limpiar_y_optimizar_descripcion(texto_sucio):
    """Limpia la descripción para que la IA busque mejor"""
    if pd.isna(texto_sucio): return "Producto desconocido"
    
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    prompt = f"""
    Traduce esta descripción técnica a una frase comercial para Uruguay:
    '{texto_sucio}'
    REGLAS: Responde SOLAMENTE con la frase optimizada sin códigos internos.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        return response.choices[0].message.content
    except:
        return str(texto_sucio).replace("-", " ")

def ejecutar_analisis_ia(sku, descripcion_original):
    """Analiza el mercado uruguayo"""
    # LIMPIEZA CRÍTICA: Quitamos el apóstrofe o coma que pusimos para el Excel
    sku_limpio = str(sku).replace("'", "").replace("´", "").strip()
    desc_optima = limpiar_y_optimizar_descripcion(descripcion_original)
    
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    prompt_usuario = f"""
    Producto: {desc_optima} (SKU: {sku_limpio})
    Busca competidores en Uruguay y responde en JSON:
    {{
        "match_nombre": "Nombre comercial",
        "precio_competidor": 0.0,
        "moneda": "USD",
        "unidad_empaque": "Presentación",
        "es_oferta": false,
        "sugerencia": "Acción",
        "tienda": "Competidor"
    }}
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt_usuario}],
            response_format={ "type": "json_object" }
        )
        data = json.loads(response.choices[0].message.content)
        data['desc_busqueda'] = desc_optima
        data['sku_procesado'] = sku_limpio
        return data
    except:
        return None

def procesar_lote_industrial(df):
    resultados = []
    progreso = st.progress(0)
    
    # MAPEADO FLEXIBLE: Buscamos tus columnas actuales
    posibles_skus = ['Nombre', 'Material', 'SKU', 'Codigo']
    posibles_descs = ['Especificación', 'Descripción', 'Texto breve de material', 'Desc']
    
    col_sku = next((c for c in posibles_skus if c in df.columns), df.columns[0])
    col_desc = next((c for c in posibles_descs if c in df.columns), df.columns[1])

    for index, row in df.iterrows():
        progreso.progress((index + 1) / len(df))
        
        # Saltamos filas vacías
        if pd.isna(row[col_sku]) and pd.isna(row[col_desc]):
            continue
            
        datos = ejecutar_analisis_ia(row[col_sku], row[col_desc])
        
        if datos:
            resultados.append({
                "SKU Original": datos['sku_procesado'],
                "Producto": datos['desc_busqueda'],
                "Competidor": datos['tienda'],
                "Precio Mercado": f"{datos['moneda']} {datos['precio_competidor']}",
                "Sugerencia": datos['sugerencia']
            })
    return resultados
