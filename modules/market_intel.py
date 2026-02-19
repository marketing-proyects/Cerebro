import streamlit as st
import pandas as pd
from io import BytesIO
from modules.ai_engine import procesar_lote_industrial

def mostrar_investigacion():
    # Encabezado con título y botón de Limpieza
    col_t, col_r = st.columns([3, 1])
    with col_t:
        st.markdown("<h1 style='margin:0'>📊 Investigación de Mercado</h1>", unsafe_allow_html=True)
    with col_r:
        if st.button("🧹 Limpiar Búsqueda", type="secondary", use_container_width=True):
            # 1. Limpiamos la caché técnica
            st.cache_data.clear()
            
            # 2. Borramos los datos y el ARCHIVO visual
            keys_to_reset = [
                'resultados_investigacion', 
                'ultimos_resultados', 
                'df_mkt_actual', 
                'precios_mkt', 
                'nombres_seleccionados',
                'invest_v_final'
            ]
            for key in keys_to_reset:
                if key in st.session_state:
                    del st.session_state[key]
            
            st.rerun()

    st.divider()
    
    # --- AVISO DE TIEMPO DE ENFRIAMIENTO PARA LA IA ---
    st.info("⏱️ **Aviso de Sistema:** Para evitar bloqueos de seguridad por parte de las Inteligencias Artificiales, por favor **AGUARDE AL MENOS 2 MINUTOS** antes de iniciar un nuevo análisis de mercado.")
    
    archivo = st.file_uploader("Subir Inventario", type=['xlsx', 'xlsm'], key="invest_v_final")
    
    if archivo:
        df = pd.read_excel(archivo, dtype=str, engine='openpyxl')
        
        if st.button("INICIAR INVESTIGACIÓN ESTRATÉGICA"):
            with st.status("🕵️ Investigando con Multi-IA...", expanded=True) as status:
                resultados = procesar_lote_industrial(df)
                st.session_state['resultados_investigacion'] = resultados 
                st.session_state['ultimos_resultados'] = resultados
                status.update(label="✅ Análisis Completo", state="complete", expanded=False)

        # Visualización y Blindaje
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
