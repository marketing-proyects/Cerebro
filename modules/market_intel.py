import streamlit as st
import pandas as pd
from io import BytesIO
from modules.ai_engine import procesar_lote_industrial

def mostrar_investigacion():
    st.markdown("<h1>📊 Investigación de Mercado</h1>", unsafe_allow_html=True)
    
    archivo = st.file_uploader("Subir Inventario", type=['xlsx', 'xlsm'], key="invest_v_definitiva")
    
    if archivo:
        df = pd.read_excel(archivo, dtype=str, engine='openpyxl')
        st.write(f"### 🔍 Vista previa ({len(df)} artículos)")
        st.dataframe(df, use_container_width=True, height=350)
        
        if st.button("INICIAR INVESTIGACIÓN ESTRATÉGICA"):
            resultados = procesar_lote_industrial(df)
            
            if resultados:
                st.success(f"✅ Análisis finalizado: {len(resultados)} artículos.")
                df_res = pd.DataFrame(resultados)
                st.dataframe(df_res, use_container_width=True)
                
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df_res.to_excel(writer, index=False)
                
                st.download_button(
                    label="📥 DESCARGAR REPORTE EXCEL",
                    data=output.getvalue(),
                    file_name="Reporte_Mercado_Uruguay.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
