import streamlit as st
from modules.auth_manager import gestionar_login

st.set_page_config(page_title="CEREBRO - WÜRTH", page_icon="🧠", layout="wide")

# Estilos globales de la plataforma
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #333333; }
    h1 { color: #ED1C24 !important; }
    div.stButton > button { background-color: #ED1C24 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

if gestionar_login():
    # Barra lateral de navegación
    st.sidebar.title("🧠 CEREBRO")
    st.sidebar.write(f"Usuario: **{st.session_state['username']}**")
    st.sidebar.divider()
    
    # Solo mostramos los módulos que el usuario tiene permitidos
    opciones = st.session_state.get("permisos", [])
    modulo = st.sidebar.radio("Navegación:", opciones)
    
    st.sidebar.divider()
    if st.sidebar.button("CERRAR SESIÓN"):
        st.session_state["autenticado"] = False
        st.rerun()

    # CARGA DE MÓDULOS INDEPENDIENTES
    if modulo == "Investigación de Mercado":
        from modules.market_intel import mostrar_investigacion
        mostrar_investigacion()
        
    elif modulo == "Fijación de Precios":
        st.markdown("<h1>💰 Fijación de Precios</h1>", unsafe_allow_html=True)
        st.info("Módulo de Pricing: Aquí integraremos las fórmulas de margen y costos.")
        # Próximo paso: from modules.pricing import mostrar_fijacion
