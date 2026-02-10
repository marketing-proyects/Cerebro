import requests
from bs4 import BeautifulSoup
import streamlit as st
import pandas as pd

def obtener_tc_real_brou():
    """Consulta la cotización de e-Brou Venta"""
    url = "https://www.brou.com.uy/web/guest/cotizaciones"
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        # Simulación de extracción del valor real del BROU
        # En producción, se usaría BeautifulSoup para capturar el valor exacto de la tabla
        return 42.85 
    except Exception:
        return 43.00 # Fallback

def procesar_investigacion_industrial(df):
    """Procesa cada fila de la ficha técnica con la IA"""
    tc_dia = obtener_tc_real_brou()
    st.sidebar.info(f"Cotización BROU aplicada: ${tc_dia}")
    
    resultados = []
    progreso = st.progress(0)
    total = len(df)

    for index, row in df.iterrows():
        progreso.progress((index + 1) / total)
        
        # Extraemos las celdas independientes
        nombre = row['Nombre']
        espec = row['Especificación']
        material = row['Material/Norma']
        ues = [row['UE 1'], row['UE 2'], row['UE 3']]
        url_comp = row['URL Competidor']

        # Lógica de razonamiento del Experto (Simulada para integración)
        # Aquí la IA compararía (Nombre + Espec + Material) contra la web
        datos_ia = {
            "tienda": "Ferretería Industrial UY",
            "precio_encontrado": 1200.0,
            "moneda": "USD",
            "ue_detectada": 100,
            "es_oferta": True,
            "alerta": "OFERTA: Descuento por liquidación de stock.",
            "confianza": 0.98
        }

        # Cálculo de Precio Unitario Competidor (con T/C si es USD)
        precio_en_pesos = datos_ia["precio_encontrado"]
        if datos_ia["moneda"] == "USD":
            precio_en_pesos = datos_ia["precio_encontrado"] * tc_dia
        
        precio_unit_comp = precio_en_pesos / datos_ia["ue_detectada"]
        
        # Comparación contra la UE 1 del usuario (Precio Propio / Cantidad UE 1)
        precio_unit_propio = row['Precio Propio (Ref)'] / ues[0]

        resultados.append({
            "Producto": f"{nombre} {espec}",
            "Material": material,
            "Precio Unit. Propio": round(precio_unit_propio, 2),
            "Precio Unit. Comp.": round(precio_unit_comp, 2),
            "Gap %": round(((precio_unit_comp - precio_unit_propio) / precio_unit_propio) * 100, 2),
            "Tienda": datos_ia["tienda"],
            "Formato Rival": f"Pack x{datos_ia['ue_detectada']}",
            "Es Oferta": datos_ia["es_oferta"],
            "Alerta": datos_ia["alerta"],
            "Link": url_comp
        })
    
    return resultados
