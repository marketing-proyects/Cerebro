import streamlit as st
import pandas as pd
from modules.auth_manager import gestionar_login
from modules.ai_engine import procesar_lote_industrial

st.set_page_config(page_title="CEREBRO - WÜRTH", page_icon="🧠", layout="wide")

# Ejecutamos la lógica de login
gestionar_login()

# Verificamos si el usuario logró entrar mediante el estado de sesión
if st.session_state.get("authentication_status"):
    usuario = st.session_state.get("username")
    st.sidebar.success(f"Sesión: {usuario}")
    
    st.title("🧠 CEREBRO SISTEMA")
    
    archivo = st.file_uploader("Cargar Inventario", type=['xlsx'])
    if archivo:
        df = pd.read_excel(archivo)
        st.dataframe(df.head(10))
        
        if st.button("EJECUTAR INVESTIGACIÓN"):
            with st.spinner("Analizando mercado..."):
                resultados = procesar_lote_industrial(df)
            st.success("FINALIZADO")
            st.dataframe(pd.DataFrame(resultados))

elif st.session_state.get("authentication_status") is False:
    st.error("Usuario o contraseña incorrectos")
else:
    st.info("Por favor, ingrese sus credenciales.")
