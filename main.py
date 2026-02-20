import streamlit as st
import os

# 1. CONFIGURACIÓN DE PÁGINA: Favicon actualizado
# El archivo debe llamarse 'favicon_wurth.png' y estar en la misma carpeta que este script
icon_path = "favicon_wurth.png"

st.set_page_config(
    page_title="SISTEMA CEREBRO - WÜRTH", 
    page_icon=icon_path if os.path.exists(icon_path) else "👁️‍🗨️", 
    layout="wide"
)

# 2. Importación de todos los módulos de la aplicación
from modules.auth_manager import gestionar_login
from modules.pricing_logic import mostrar_fijacion_precios
from modules.market_intel import mostrar_investigacion
from modules.liquidation_manager import mostrar_modulo_liquidation

# 3. Estilos visuales de Würth (Colores corporativos)
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #333333; }
    h1 { color: #ED1C24 !important; }
    div.stButton > button { background-color: #ED1C24 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# 4. Lógica de autenticación y navegación
if gestionar_login():
    st.sidebar.title('INTELIGENCIA DE MARKETING Y MERCADO "CEREBRO"')
    st.sidebar.write(f"Usuario: **{st.session_state.get('username', 'admin')}**")
    st.sidebar.divider()
    
    # Nombres de módulos actualizados
    modulos_disponibles = [
        "Investigación de Mercado", 
        "Fijación de Precios", 
        "Liquidación (Prox. vencimientos)"
    ]
    
    # Obtenemos permisos del session_state
    modulos = st.session_state.get("permisos", modulos_disponibles)
    
    # CAMBIO: De "Navegación" a "Módulos"
    seleccion = st.sidebar.radio("Módulos:", modulos)
    
    st.sidebar.divider()
    if st.sidebar.button("CERRAR SESIÓN"):
        st.session_state["autenticado"] = False
        st.rerun()

    # Enrutamiento con el nombre actualizado
    if seleccion == "Investigación de Mercado":
        mostrar_investigacion()
        
    elif seleccion == "Fijación de Precios":
        mostrar_fijacion_precios()

    elif seleccion == "Liquidación (Prox. vencimientos)": 
        mostrar_modulo_liquidation() 

    else:
        st.error("No tienes permisos asignados. Contacta al administrador.")
