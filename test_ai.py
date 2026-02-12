import streamlit as st
import time
from modules.ai_engine import ejecutar_analisis_ia

def probar_conexion_ia():
    st.markdown("### 🧪 Test de Diagnóstico de IA")
    st.write("Esta prueba validará la conexión con la API y el análisis de la URL de España.")
    
    # Datos de prueba basados en tu imagen
    test_sku = "893226101"
    test_desc = "Adhesivo estructural MS, adhesivo de espejo"
    test_url = "https://www.wurth.es/adhesivo-ms-instant-espejos-290ml"

    if st.button("EJECUTAR PRUEBA DE DETECTIVE"):
        # El Spinner indica que el proceso está vivo
        with st.spinner("🕵️ El Cerebro está analizando la URL de España..."):
            start_time = time.time()
            
            # Llamada al motor de IA
            resultado = ejecutar_analisis_ia(test_sku, test_desc, test_url)
            
            end_time = time.time()
            duracion = round(end_time - start_time, 2)

        if resultado and resultado.get("comp") != "Info no encontrada":
            st.success(f"✅ ¡Conexión Exitosa! Tiempo de respuesta: {duracion} segundos.")
            st.json(resultado) # Muestra el JSON técnico que devuelve la IA
        else:
            st.error("❌ La IA respondió, pero no logró encontrar equivalentes en Uruguay.")
            st.info("Sugerencia: Revisa que el prompt en ai_engine.py sea el de la versión 'Detective'.")

# Llamar a esta función en tu main.py para probar
