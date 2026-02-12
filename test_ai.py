import streamlit as st
import time
from modules.ai_engine import ejecutar_analisis_ia

def probar_conexion_ia():
    st.markdown("### 🧪 Test de Diagnóstico de IA (Modo Detective)")
    
    test_sku = "893226101"
    test_desc = "Adhesivo estructural MS, adhesivo de espejo"
    test_url = "https://www.wurth.es/adhesivo-ms-instant-espejos-290ml"

    if st.button("EJECUTAR PRUEBA DE DETECTIVE"):
        with st.spinner("🕵️ El Cerebro está analizando la URL y buscando competencia en Uruguay..."):
            resultado = ejecutar_analisis_ia(test_sku, test_desc, test_url)

        if resultado and resultado.get("comp") != "Info no encontrada":
            st.success("✅ ¡El detective ha encontrado competencia en Uruguay!")
            st.json(resultado)
        else:
            st.error("❌ La IA no logró cruzar la información técnica con el mercado uruguayo.")
            st.info("Asegúrate de que ai_engine.py tenga el prompt actualizado de 'Detective'.")
