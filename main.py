import streamlit as st
import pandas as pd
from modules.auth_manager import gestionar_login
from modules.data_processor import cargar_archivo, validar_columnas
from modules.ai_engine import procesar_investigacion_industrial

st.set_page_config(page_title="Cerebro Industrial", page_icon="🔧", layout="wide")

autenticado, usuario = gestionar_login()

if autenticado:
    st.sidebar.title(f"Sesión: {usuario}")
    st.title("🔧 Cerebro Industrial: Inteligencia Würth")
    st.info("Análisis de mercado basado en fichas técnicas y cotización BROU.")

    df_usuario = cargar_archivo()
    
    if df_usuario is not None:
        columnas_req = [
            "Nombre", "Especificación", "Material/Norma", 
            "UE 1", "UE 2", "UE 3", 
            "Precio Propio (Ref)", "URL Competidor"
        ]
        
        if validar_columnas(df_usuario, columnas_req):
            st.write("### Ficha Técnica Cargada")
            st.dataframe(df_usuario, use_container_width=True)
            
            if st.button("🚀 Iniciar Análisis de Mercado (Comparación Unit.)"):
                with st.spinner("IA analizando materiales y formatos de empaque..."):
                    resultados = procesar_investigacion_industrial(df_usuario)
                
                st.success("✅ Análisis Completo")
                df_final = pd.DataFrame(resultados)

                # Alertas de Ofertas y Empaques (Punto 1 y 2 de la solicitud)
                for _, row in df_final.iterrows():
                    if row["Es Oferta"]:
                        st.warning(f"📢 **{row['Producto']}**: {row['Alerta']}")
                
                st.write("### Comparativa de Precios Unitarios (UYU)")
                st.dataframe(df_final, use_container_width=True)

                # Exportación
                csv = df_final.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Descargar Reporte de Precios Industrial",
                    data=csv,
                    file_name='reporte_industrial_uy.csv',
                    mime='text/csv',
                )

    if st.sidebar.button("Salir"):
        st.session_state["authenticator"].logout('main')
        st.rerun()
