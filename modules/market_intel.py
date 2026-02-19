import streamlit as st
import pandas as pd
from io import BytesIO
from modules.ai_engine import procesar_lote_industrial

def mostrar_investigacion():
    st.markdown("<h1>📊 Investigación de Mercado</h1>", unsafe_allow_html=True)
    
    st.info("💡 **Nota:** Para iniciar una nueva búsqueda desde cero, por favor presione la tecla **F5** (o actualice la pestaña en su navegador) para limpiar los resultados anteriores.")
    
    st.divider()
    
    archivo = st.file_uploader("Subir Inventario", type=['xlsx', 'xlsm'], key="invest_v_final")
    
    if archivo:
        df = pd.read_excel(archivo, dtype=str, engine='openpyxl')
        
        if st.button("INICIAR INVESTIGACIÓN ESTRATÉGICA"):
            with st.status("🕵️ Investigando con Multi-IA...", expanded=True) as status:
                resultados = procesar_lote_industrial(df)
                st.session_state['resultados_investigacion'] = resultados 
                st.session_state['ultimos_resultados'] = resultados
                status.update(label="✅ Análisis Completo", state="complete", expanded=False)

        # BLINDAJE: Verificamos de forma segura si la IA devolvió datos
        if 'ultimos_resultados' in st.session_state:
            datos_mkt = st.session_state['ultimos_resultados']
            
            if isinstance(datos_mkt, (list, dict, pd.DataFrame)) and len(datos_mkt) > 0:
                df_res = pd.DataFrame(datos_mkt)
                st.divider()
                st.write("### 📈 Resultados de la Competencia")
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
            elif datos_mkt is not None and len(datos_mkt) == 0:
                st.warning("⚠️ Análisis completado, pero la IA no devolvió resultados para este inventario.")
