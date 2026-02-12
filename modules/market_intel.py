import streamlit as st
import pandas as pd
from io import BytesIO
from modules.ai_engine import procesar_lote_industrial

def mostrar_investigacion():
    st.markdown("<h1>📊 Investigación de Mercado</h1>", unsafe_allow_html=True)
    
    archivo = st.file_uploader("Subir Inventario", type=['xlsx', 'xlsm'], key="invest_vfinal")
    
    if archivo:
        df = pd.read_excel(archivo, dtype=str, engine='openpyxl')
        st.dataframe(df, use_container_width=True, height=300)
        
        if st.button("INICIAR INVESTIGACIÓN ESTRATÉGICA"):
            # Generamos el contenedor para la tabla final ANTES de procesar
            placeholder_tabla = st.empty()
            
            resultados = procesar_lote_industrial(df)
            
            if resultados:
                st.success(f"✅ Proceso finalizado: {len(resultados)} artículos analizados.")
                df_res = pd.DataFrame(resultados)
                
                # Mostramos la tabla
                st.dataframe(df_res, use_container_width=True)
                
                # Generamos el Excel de descarga
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df_res.to_excel(writer, index=False)
                
                st.download_button(
                    label="📥 DESCARGAR REPORTE EXCEL",
                    data=output.getvalue(),
                    file_name="Analisis_Mercado_Uruguay.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.error("No se pudieron generar resultados. Verifique la conexión con las IAs.")
