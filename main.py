import streamlit as st
import pandas as pd
from modules.auth_manager import gestionar_login
from modules.ai_engine import procesar_lote_industrial

st.set_page_config(page_title="CEREBRO - WÜRTH", page_icon="🧠", layout="wide")

# Estilos Generales Würth (Rojo y Negro)
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #FFFFFF; }
    h1 { color: #ED1C24; }
    div.stButton > button { background-color: #ED1C24 !important; color: white !important; }
    div.stButton > button p { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# Ejecutamos el login (Si devuelve True, muestra el sistema)
if gestionar_login():
    # Encabezado sutil
    col_l, col_t = st.columns([1, 10])
    with col_l:
        st.image("https://upload.wikimedia.org/wikipedia/commons/b/be/W%C3%BCrth_logo.svg", width=70)
    with col_t:
        st.markdown("<h1>🧠 CEREBRO SISTEMA</h1>", unsafe_allow_html=True)
    
    st.write("---")

    # Pestañas operativas (Sin pestaña de Marca)
    tab1, tab2, tab3 = st.tabs(["📊 MERCADO", "📦 LOGÍSTICA", "💼 COMERCIAL"])

    with tab1:
        st.subheader("Investigación Estratégica")
        archivo = st.file_uploader("Subir Inventario", type=['xlsx'], key="up_main")
        if archivo:
            # Aseguramos que los códigos de Würth no pierdan el cero inicial
            df = pd.read_excel(archivo, dtype={'Material': str})
            st.dataframe(df.head(10), use_container_width=True)
            if st.button("PROCESAR ANÁLISIS"):
                with st.spinner("IA analizando competencia..."):
                    resultados = procesar_lote_industrial(df)
                st.success("Análisis completado")

    with tab2: st.info("Módulo de Optimización de Inventario")
    with tab3: st.info("Módulo de Ventas y Márgenes")

    # Barra lateral
    st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/b/be/W%C3%BCrth_logo.svg", width=100)
    if st.sidebar.button("CERRAR SESIÓN"):
        st.session_state["autenticado"] = False
        st.rerun()
