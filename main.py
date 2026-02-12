import streamlit as st
from modules.auth_manager import gestionar_login

st.set_page_config(page_title="CEREBRO - WÜRTH", page_icon="🧠", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #333333; }
    h1 { color: #ED1C24 !important; }
    div.stButton > button { background-color: #ED1C24 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

if gestionar_login():
    st.sidebar.title("🧠 CEREBRO")
    st.sidebar.write(f"Usuario: **{st.session_state.get('username', 'admin')}**")
    st.sidebar.divider()
    
    modulos = st.session_state.get("permisos", ["Investigación de Mercado"])
    seleccion = st.sidebar.radio("Navegación:", modulos)
    
    st.sidebar.divider()
    if st.sidebar.button("CERRAR SESIÓN"):
        st.session_state["autenticado"] = False
        st.rerun()

    if seleccion == "Investigación de Mercado":
        from modules.market_intel import mostrar_investigacion
        mostrar_investigacion()
    elif seleccion == "Fijación de Precios":
        st.markdown("<h1>💰 Fijación de Precios</h1>", unsafe_allow_html=True)
        st.info("Módulo listo para recibir lógica de márgenes.")
