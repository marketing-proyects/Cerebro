import streamlit as st
from modules.auth_manager import gestionar_login
from modules.data_processor import cargar_archivo, validar_columnas

# 1. Configuración de la interfaz (Look & Feel)
st.set_page_config(page_title="Cerebro - Inteligencia de Mercado", layout="wide")

# 2. Control de Acceso
autenticado, usuario = gestionar_login()

if autenticado:
    # --- Interfaz una vez logueado ---
    st.sidebar.success(f"Sesión activa: {usuario}")
    st.title("🧠 Cerebro: Market Intel AI")
    st.markdown("---")

    # 3. Flujo de Trabajo: Carga de Datos
    st.header("1. Carga de datos de competencia")
    df_usuario = cargar_archivo()
    
    if df_usuario is not None:
        # Definimos las columnas que el usuario DEBE tener en su Excel
        # Puedes ajustar estos nombres según lo que prefieras pedir
        columnas_req = ["SKU", "Producto", "Precio Propio", "URL Competidor"]
        
        if validar_columnas(df_usuario, columnas_req):
            st.write("### Vista Previa de la Investigación")
            st.dataframe(df_usuario, use_container_width=True)
            
            # Botón para activar el siguiente paso (Motor de IA)
            if st.button("🚀 Iniciar Escaneo de Precios"):
                st.info("Conectando con el Motor de IA para analizar links...")
                # Aquí llamaremos al módulo de IA en el siguiente paso
    
    # Botón para salir en la barra lateral
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state["authenticator"].logout('main')
