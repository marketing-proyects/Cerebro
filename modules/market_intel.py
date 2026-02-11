import streamlit as st
import pandas as pd
from io import BytesIO
from modules.ai_engine import procesar_lote_industrial

def mostrar_investigacion():
    st.markdown("<h1>📊 Investigación de Mercado</h1>", unsafe_allow_html=True)
    st.write("Analice posicionamiento, precios y competencia en el mercado uruguayo.")
    st.write("---")

    # 1. Cargador de archivos
    archivo = st.file_uploader("Subir Inventario (.xlsx, .xlsm)", type=['xlsx', 'xlsm'], key="up_intel_final")
    
    if archivo:
        # Cargamos el archivo manteniendo tipos de datos
        df = pd.read_excel(archivo, dtype=str, engine='openpyxl')
        
        # Mapeo flexible de columnas para que el usuario no tenga que renombrar su Excel
        mapeo = {'Nombre': 'Material', 'Especificación': 'Descripción', 'URL': 'Enlace'}
        df = df.rename(columns=mapeo)
        
        st.write("### 🔍 Vista previa de productos a investigar")
        st.dataframe(df.head(10), use_container_width=True)
        
        # 2. Botón de Ejecución
        if st.button("INICIAR INVESTIGACIÓN ESTRATÉGICA"):
            with st.spinner("El Cerebro está rastreando tiendas, importadores y precios en Uruguay..."):
                resultados = procesar_lote_industrial(df)
            
            if resultados:
                st.success("✅ INVESTIGACIÓN FINALIZADA CON ÉXITO")
                df_resultados = pd.DataFrame(resultados)
                
                # Mostramos los resultados en pantalla
                st.write("### 📋 Resultados Detectados")
                st.dataframe(df_resultados, use_container_width=True)
                
                # 3. Lógica para Generar Excel en Memoria
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df_resultados.to_excel(writer, index=False, sheet_name='Investigación_Cerebro')
                    # Opcional: Auto-ajuste de columnas (XlsxWriter lo permite)
                    workbook  = writer.book
                    worksheet = writer.sheets['Investigación_Cerebro']
                    format_header = workbook.add_format({'bold': True, 'bg_color': '#ED1C24', 'font_color': 'white'})
                    
                    for col_num, value in enumerate(df_resultados.columns.values):
                        worksheet.write(0, col_num, value, format_header)
                
                processed_data = output.getvalue()

                # 4. Botón de Descarga
                st.download_button(
                    label="📥 DESCARGAR REPORTE EN EXCEL",
                    data=processed_data,
                    file_name="Reporte_Investigacion_Wurth.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.error("No se pudo generar el reporte. Verifique que la descripción de los artículos sea clara.")
