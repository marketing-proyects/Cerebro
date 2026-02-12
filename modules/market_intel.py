import streamlit as st
import pandas as pd
from io import BytesIO
from modules.ai_engine import procesar_lote_industrial

def mostrar_investigacion():
    st.markdown("<h1>📊 Investigación de Mercado</h1>", unsafe_allow_html=True)
    st.write("Identifique competidores, marcas y precios en el mercado uruguayo.")
    st.write("---")

    archivo = st.file_uploader("Subir Inventario (.xlsx, .xlsm)", type=['xlsx', 'xlsm'], key="intel_uploader")
    
    if archivo:
        df = pd.read_excel(archivo, dtype=str, engine='openpyxl')
        
        # Mapeo flexible de columnas
        mapeo = {'Nombre': 'Material', 'Especificación': 'Descripción', 'URL': 'Enlace'}
        df = df.rename(columns=mapeo)
        
        st.write("### 🔍 Vista previa de datos")
        st.dataframe(df.head(10), use_container_width=True)
        
        if st.button("INICIAR INVESTIGACIÓN ESTRATÉGICA"):
            with st.spinner("La IA está analizando el mercado uruguayo..."):
                resultados = procesar_lote_industrial(df)
            
            if resultados:
                st.success("✅ ANÁLISIS COMPLETADO")
                df_res = pd.DataFrame(resultados)
                st.dataframe(df_res, use_container_width=True)
                
                # Generador de Excel con formato
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df_res.to_excel(writer, index=False, sheet_name='Resultados_Cerebro')
                
                st.download_button(
                    label="📥 DESCARGAR REPORTE EN EXCEL",
                    data=output.getvalue(),
                    file_name="Reporte_Competencia_Wurth.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.warning("No se encontraron resultados comerciales.")
