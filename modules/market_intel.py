import streamlit as st
import pandas as pd
from modules.ai_engine import procesar_lote_industrial

def mostrar_investigacion():
    st.markdown("<h1>📊 Investigación de Mercado</h1>", unsafe_allow_html=True)
    st.write("---")

    archivo = st.file_uploader("Subir Inventario (.xlsx, .xlsm)", type=['xlsx', 'xlsm'], key="up_intel")
    
    if archivo:
        df = pd.read_excel(archivo, dtype=str, engine='openpyxl')
        
        # Mapeo de tus columnas del Excel
        mapeo = {'Nombre': 'Material', 'Especificación': 'Descripción'}
        df = df.rename(columns=mapeo)
        
        st.write("### 🔍 Vista previa de productos")
        st.dataframe(df.head(10), use_container_width=True)
        
        if st.button("BUSCAR COMPETENCIA"):
            with st.spinner("La IA está rastreando el mercado uruguayo..."):
                resultados = procesar_lote_industrial(df)
            
            if resultados:
                st.success("ANÁLISIS COMPLETADO")
                st.dataframe(pd.DataFrame(resultados), use_container_width=True)
            else:
                st.warning("No se encontraron resultados comerciales.")
