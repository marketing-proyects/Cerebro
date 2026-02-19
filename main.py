import streamlit as st
from modules.auth_manager import gestionar_login
# 1. Agregamos la importación del nuevo módulo aquí
from modules.pricing_logic import mostrar_fijacion_precios 

st.set_page_config(page_title="CEREBRO - WÜRTH", page_icon="👁️‍🗨️", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #333333; }
    h1 { color: #ED1C24 !important; }
    div.stButton > button { background-color: #ED1C24 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

if gestionar_login():
    st.sidebar.title("INTELIGENCIA DE MARKETING Y MERCADO "CEREBRO")
    st.sidebar.write(f"Usuario: **{st.session_state.get('username', 'admin')}**")
    st.sidebar.divider()
    
    # Asegúrate de que "Fijación de Precios" esté en la lista de permisos de tu base de datos o auth_manager
    modulos = st.session_state.get("permisos", ["Investigación de Mercado", "Fijación de Precios"])
    seleccion = st.sidebar.radio("Navegación:", modulos)
    
    st.sidebar.divider()
    if st.sidebar.button("CERRAR SESIÓN"):
        st.session_state["autenticado"] = False
        st.rerun()

    if seleccion == "Investigación de Mercado":
        from modules.market_intel import mostrar_investigacion
        mostrar_investigacion()
        
    # 2. Reemplazamos el texto genérico por la función real
    elif seleccion == "Fijación de Precios":
        mostrar_fijacion_precios()
