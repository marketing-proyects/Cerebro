import streamlit as st
from modules.auth_manager import gestionar_login

# Configuración inicial de la página
st.set_page_config(page_title="CEREBRO - WÜRTH", page_icon="🧠", layout="wide")

# Estilos globales para limpieza visual y eliminar el "0"
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #333333; }
    h1 { color: #ED1C24 !important; }
    div.stButton > button { background-color: #ED1C24 !important; color: white !important; }
    /* Ajuste para evitar basura visual en el header */
    .block-container { padding-top: 2rem; }
    </style>
    """, unsafe_allow_html=True)

if gestionar_login():
    # Sidebar: Navegación y Usuario
    st.sidebar.title("🧠 CEREBRO")
    st.sidebar.write(f"Usuario: **{st.session_state.get('username', 'admin')}**")
    st.sidebar.divider()
    
    # Selector de módulos según permisos del usuario
    modulos_permitidos = st.session_state.get("permisos", ["Investigación de Mercado"])
    seleccion = st.sidebar.radio("Navegación:", modulos_permitidos)
    
    st.sidebar.divider()
    
    # --- SECCIÓN DE DIAGNÓSTICO ---
    # Invocamos el archivo test_ai.py que creaste en la raíz
    try:
        from test_ai import probar_conexion_ia
        if st.sidebar.checkbox("🔍 Activar Test de IA"):
            probar_conexion_ia()
            st.sidebar.divider()
    except ImportError:
        st.sidebar.warning("Archivo test_ai.py no detectado en la raíz.")
    # ------------------------------

    if st.sidebar.button("CERRAR SESIÓN"):
        st.session_state["autenticado"] = False
        st.rerun()

    # Carga dinámica del módulo seleccionado
    if seleccion == "Investigación de Mercado":
        from modules.market_intel import mostrar_investigacion
        mostrar_investigacion()
        
    elif seleccion == "Fijación de Precios":
        st.markdown("<h1>💰 Fijación de Precios</h1>", unsafe_allow_html=True)
        st.info("Módulo en desarrollo: Aquí se integrará la lógica de márgenes y sugerencias de precios.")
