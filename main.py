import streamlit as st
import pandas as pd
from modules.auth_manager import gestionar_login
from modules.data_processor import cargar_archivo
from modules.ai_engine import procesar_lote_industrial

st.set_page_config(page_title="CEREBRO - WÜRTH - MARKET INTEL", page_icon="🧠", layout="wide")

# Estilos
st.markdown("""
    <style>
    .stApp { background-color: #121417; color: #FFFFFF; }
    h1 { color: #00FBFF; text-shadow: 0px 0px 8px rgba(0, 251, 255, 0.2); }
    .stButton>button { border: 1px solid #00FBFF; color: #00FBFF; background: transparent; width: 100%; }
    .stButton>button:hover { box-shadow: 0px 0px 15px #00FBFF; color: #121417; background: #00FBFF; }
    </style>
    """, unsafe_allow_html=True)

# Ejecutamos la lógica de login
gestionar_login()

# Verificamos si la autenticación fue exitosa
if st.session_state.get("authentication_status"):
    usuario = st.session_state.get("username")
    
    st.sidebar.success(f"Sesión activa: {usuario}")
    st.markdown("<h1>🧠 CEREBRO SISTEMA ⚙️</h1>", unsafe_allow_html=True)
    
    archivo = st.file_uploader("Cargar Inventario", type=['xlsx'])
    
    if archivo:
        df = pd.read_excel(archivo)
        st.dataframe(df.head(10), use_container_width=True)
        
        if st.button("EJECUTAR INVESTIGACIÓN DE MERCADO"):
            with st.spinner("Analizando..."):
                resultados = procesar_lote_industrial(df)
            st.success("FINALIZADO")
            st.dataframe(pd.DataFrame(resultados))

elif st.session_state.get("authentication_status") is False:
    st.error("Usuario o contraseña incorrectos")
else:
    st.info("Sistema Protegido. Ingrese credenciales.")
