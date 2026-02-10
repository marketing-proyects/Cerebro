import streamlit as st
import pandas as pd
from modules.auth_manager import gestionar_login
from modules.data_processor import cargar_archivo, validar_columnas
from modules.ai_engine import procesar_lista_productos

# Configuración profesional de la página
st.set_page_config(page_title="Cerebro - Market Intel", page_icon="🧠", layout="wide")

# Autenticación modular
autenticado, usuario = gestionar_login()

if autenticado:
    st.sidebar.title(f"Usuario: {usuario}")
    st.title("🧠 Cerebro: Inteligencia de Mercado Uruguay")
    st.markdown("---")

    # 1. Carga de datos
    st.header("1. Subida de Inventario")
    df_usuario = cargar_archivo()
    
    if df_usuario is not None:
        columnas_req = ["SKU", "Producto", "Precio Propio", "URL Competidor"]
        
        if validar_columnas(df_usuario, columnas_req):
            st.write("### Datos cargados para análisis")
            st.dataframe(df_usuario, use_container_width=True)
            
            # 2. Ejecución del motor con experto en mercado
            if st.button("🚀 Iniciar Investigación de Mercado"):
                with st.spinner("La IA está analizando empaques, monedas y ofertas..."):
                    lista_resultados = procesar_lista_productos(df_usuario)
                
                st.success("✅ Análisis de mercado finalizado")
                df_final = pd.DataFrame(lista_resultados)

                # 3. Alertas Visuales (Punto 1 de tu solicitud)
                for index, row in df_final.iterrows():
                    if row["Es Oferta"]:
                        st.warning(f"📢 **{row['Producto']}**: {row['Alerta']}")
                    if row["U.E."] > 1:
                        st.info(f"📦 **{row['Producto']}**: Detectado formato pack x{row['U.E.']}. Precio normalizado a unidad.")

                # 4. Tabla de Decisiones
                st.write("### Tabla Comparativa de Precios Unitarios")
                st.dataframe(df_final, use_container_width=True)

                # 5. Exportación
                csv = df_final.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Descargar Reporte para Toma de Decisiones",
                    data=csv,
                    file_name='reporte_mercado_uy.csv',
                    mime='text/csv',
                )

    if st.sidebar.button("Cerrar Sesión"):
        st.session_state["authenticator"].logout('main')
        st.rerun()
else:
    st.info("Sistema Privado. Por favor inicie sesión para continuar.")
