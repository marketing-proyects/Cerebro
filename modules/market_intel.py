import streamlit as st
import pandas as pd
from io import BytesIO
from modules.ai_engine import procesar_lote_industrial

def mostrar_investigacion():
    st.markdown("<h1>📊 Investigación de Mercado (Multi-IA)</h1>", unsafe_allow_html=True)
    st.info("Sistema conectado a Gemini (Google) y GPT-4o (Copilot) para máxima precisión.")
    
    archivo = st.file_uploader("Subir Inventario para analizar", type=['xlsx', 'xlsm'], key="multi_ia_up")
    
    if archivo:
        df = pd.read_excel(archivo, dtype=str, engine='openpyxl')
        st.dataframe(df.head(5), use_container_width=True)
        
        if st.button("INICIAR BÚSQUEDA MULTI-IA"):
            with st.spinner("🕵️ Triangulando información en el mercado uruguayo..."):
                resultados = procesar_lote_industrial(df)
            
            if resultados:
                st.success("✅ Análisis Completo")
                df_res = pd.DataFrame(resultados)
                st.dataframe(df_res, use_container_width=True)
                
                # Botón de descarga profesional
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df_res.to_excel(writer, index=False, sheet_name='Analisis_Cerebro')
                
                st.download_button(
                    label="📥 DESCARGAR REPORTE ESTRATÉGICO",
                    data=output.getvalue(),
                    file_name="Reporte_Cerebro_MultiIA.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
