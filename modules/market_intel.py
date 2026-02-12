import streamlit as st
import pandas as pd
from io import BytesIO
from modules.ai_engine import procesar_lote_industrial

def mostrar_investigacion():
    st.markdown("<h1>📊 Investigación de Mercado</h1>", unsafe_allow_html=True)
    st.write("Detección de competencia basada en análisis técnico de URLs.")
    
    archivo = st.file_uploader("Subir Inventario (.xlsx, .xlsm)", type=['xlsx', 'xlsm'])
    
    if archivo:
        df = pd.read_excel(archivo, dtype=str, engine='openpyxl')
        st.write("### 🔍 Datos detectados")
        st.dataframe(df.head(5), use_container_width=True)
        
        if st.button("INICIAR INVESTIGACIÓN ESTRATÉGICA"):
            with st.spinner("La IA está actuando como detective de URLs..."):
                resultados = procesar_lote_industrial(df)
            
            if resultados:
                st.success("✅ Análisis completado")
                df_res = pd.DataFrame(resultados)
                st.dataframe(df_res, use_container_width=True)
                
                # Botón de descarga
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df_res.to_excel(writer, index=False)
                st.download_button(
                    label="📥 Descargar Reporte Excel",
                    data=output.getvalue(),
                    file_name="Reporte_Competencia.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
