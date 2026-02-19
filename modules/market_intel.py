import streamlit as st
import pandas as pd
from io import BytesIO
from modules.ai_engine import procesar_lote_industrial

def mostrar_investigacion():
    # Título y Botón de Refresh alineado a la derecha
    col_t, col_r = st.columns([3, 1])
    with col_t:
        st.markdown("<h1 style='margin:0'>📊 Investigación de Mercado</h1>", unsafe_allow_html=True)
    with col_r:
        if st.button("🔄 Nueva Investigación", type="primary", use_container_width=True):
            # 1. Limpieza de variables de estado
            keys_to_reset = [
                'resultados_investigacion', 
                'ultimos_resultados', 
                'df_mkt_actual', 
                'precios_mkt', 
                'nombres_seleccionados'
            ]
            for key in keys_to_reset:
                if key in st.session_state:
                    del st.session_state[key]
            
            # 2. Limpieza de CACHÉ (Vital para que no repita el resultado vacío)
            st.cache_data.clear()
            st.cache_resource.clear()
            
            # 3. Reinicio total
            st.rerun()

    st.divider()
    
    archivo = st.file_uploader("Subir Inventario", type=['xlsx', 'xlsm'], key="invest_v_final")
    
    if archivo:
        df = pd.read_excel(archivo, dtype=str, engine='openpyxl')
        
        if st.button("INICIAR INVESTIGACIÓN ESTRATÉGICA"):
            with st.status("🕵️ Investigando con Multi-IA...", expanded=True) as status:
                # Al haber limpiado el caché arriba, esta función se ejecutará como nueva
                resultados = procesar_lote_industrial(df)
                st.session_state['resultados_investigacion'] = resultados 
                st.session_state['ultimos_resultados'] = resultados
                status.update(label="✅ Análisis Completo", state="complete", expanded=False)

        if 'ultimos_resultados' in st.session_state and st.session_state['ultimos_resultados']:
            df_res = pd.DataFrame(st.session_state['ultimos_resultados'])
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
