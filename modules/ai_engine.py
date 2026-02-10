import openai
import streamlit as st

def obtener_tc_brou():
    """
    Simulación de consulta al BROU. 
    Scraper ligero para esta URL.
    """
    return 42.50  # Valor de ejemplo para Uruguay

def extraer_con_experto_mercado(url_competidor, producto_nombre, precio_propio):
    tc_dia = obtener_tc_brou()
    
    # Este es el Súper Prompt con tus nuevas reglas
    prompt = f"""
    Eres un experto en estudios de mercado en Uruguay.
    Analiza el producto: {producto_nombre} (Tu precio: {precio_propio}).
    
    REGLAS CRÍTICAS:
    1. Identifica si el precio es una OFERTA temporal (carteles de promo, liquidación).
    2. Identifica la UNIDAD DE EMPAQUE (UE). Si es un pack, divide para hallar el PRECIO UNITARIO.
    3. Si el precio está en U$S, conviértelo a Pesos usando el T/C del día: {tc_dia}.
    4. Asegúrate de que la tienda sea URUGUAYA.
    
    URL a analizar: {url_competidor}
    """
    
    # Simulación de la respuesta estructurada de la IA
    return {
        "match_nombre": "Atornilladora Brushless 20v - Oferta",
        "confianza": 0.98,
        "tienda": "Ingco / Total / Bosch / Makita",
        "moneda_original": "USD",
        "precio_publicado": 450.00,
        "unidad_empaque": 1,
        "precio_unitario_uyu": 19125.00,  # 450 * 42.50
        "tipo_precio": "Promocional", # <-- Aviso de alerta
        "alerta_promo": "⚠️ OFERTA DETECTADA: Válido hasta agotar stock web.",
        "sugerencia": "Mantener precio. La competencia está en liquidación temporal."
    }

def procesar_investigacion(df):
    resultados = []
    for _, row in df.iterrows():
        # Llamada a la lógica de experto
        datos = extraer_con_experto_mercado(row['URL Competidor'], row['Producto'], row['Precio Propio'])
        
        # Unimos tus datos con los hallazgos de la IA
        resultados.append({
            **row.to_dict(), # Mantiene tus columnas originales
            "Precio Unitario Comp.": datos["precio_unitario_uyu"],
            "Estado": datos["tipo_precio"],
            "Alerta": datos["alerta_promo"],
            "Confianza Match": f"{datos['confianza']*100}%",
            "Sugerencia IA": datos["sugerencia"]
        })
    return resultados
