import streamlit as st
import pandas as pd
from io import BytesIO
from modules.ai_engine import procesar_lote_industrial

def mostrar_investigacion():
    st.markdown("<h1>📊 Investigación de Mercado</h1>", unsafe_allow_html=True)
    st.write("Análisis profundo basado en descripción y URL técnica.")
    
    archivo = st.file_uploader("Subir Inventario (.xlsx, .xlsm)", type=['xlsx', 'xlsm'], key="invest_v3")
    
    if archivo:
        df = pd.read_excel(archivo, dtype=str, engine='openpyxl')
        st.write("### 🔍 Vista previa de carga")
        st.dataframe(df.head(5), use_container_width=True)
        
        if st.button("INICIAR INVESTIGACIÓN ESTRATÉGICA"):
            with st.spinner("🕵️ El Cerebro está analizando URLs y PDFs técnicos..."):
                resultados = procesar_lote_industrial(df)
            
            if resultados:
                st.success("✅ ANÁLISIS FINALIZADO")
                df_res = pd.DataFrame(resultados)
                st.dataframe(df_res, use_container_width=True)
                
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df_res.to_excel(writer, index=False, sheet_name='Analisis')
                
                st.download_button(
                    label="📥 DESCARGAR REPORTE EXCEL",
                    data=output.getvalue(),
                    file_name="Investigacion_Uruguay.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.warning("No se detectaron resultados. Verifique las URLs proporcionadas.")
