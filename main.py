import streamlit as st
import os

# 1. CONFIGURACIÓN DE PÁGINA: Ahora apuntando al nombre correcto
icon_path = "favicon.png"

st.set_page_config(
    page_title="SISTEMA CEREBRO - WÜRTH", 
    page_icon=icon_path if os.path.exists(icon_path) else "👁️‍🗨️", 
    layout="wide"
)

# 2. Importación de módulos
from modules.auth_manager import gestionar_login
from modules.pricing_logic import mostrar_fijacion_precios
from modules.market_intel import mostrar_investigacion
from modules.liquidation_manager import mostrar_modulo_liquidation
from modules.overstock_manager import mostrar_modulo_overstock

# 3. Estilos corporativos
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #333333; }
    h1 { color: #ED1C24 !important; }
    div.stButton > button { background-color: #ED1C24 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# 4. Lógica de acceso
if gestionar_login():
    st.sidebar.title('INTELIGENCIA DE MARKETING Y MERCADO "CEREBRO"')
    st.sidebar.write(f"Usuario: **{st.session_state.get('username', 'admin')}**")
    st.sidebar.divider()
    
    # Lista de nombres actualizados
    modulos_disponibles = [
        "Investigación de Mercado", 
        "Fijación de Precios", 
        "Liquidación (Prox. vencimientos)"
    ]
    
    modulos = st.session_state.get("permisos", modulos_disponibles)
    
    # AJUSTE: Ahora dice "Módulos:"
    seleccion = st.sidebar.radio("Módulos:", modulos)
    
    st.sidebar.divider()
    if st.sidebar.button("CERRAR SESIÓN"):
        st.session_state["autenticado"] = False
        st.rerun()

    # Enrutamiento
    if seleccion == "Investigación de Mercado":
        mostrar_investigacion()
    elif seleccion == "Fijación de Precios":
        mostrar_fijacion_precios()
    elif seleccion == "Liquidación (Prox. vencimientos)": 
        mostrar_modulo_liquidation() 
    else:
        st.error("No tienes permisos asignados.")
