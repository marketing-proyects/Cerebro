import streamlit as st
import pandas as pd
from modules.auth_manager import gestionar_login
from modules.ai_engine import procesar_lote_industrial

st.set_page_config(page_title="CEREBRO - WÜRTH", page_icon="🧠", layout="wide")

# Estilos Globales
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #FFFFFF; }
    
    /* Botones generales del sistema con texto blanco forzado */
    div.stButton > button {
        background-color: #ED1C24 !important;
        color: white !important;
    }
    div.stButton > button p { color: white !important; }

    /* Estilo Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 15px; }
    .stTabs [aria-selected="true"] { color: #ED1C24 !important; border-bottom-color: #ED1C24 !important; }
    </style>
    """, unsafe_allow_html=True)

if gestionar_login():
    # Encabezado con logo detalle
    col_l, col_t = st.columns([1, 12])
    with col_l:
        st.image("https://upload.wikimedia.org/wikipedia/commons/b/be/W%C3%BCrth_logo.svg", width=70)
    with col_t:
        st.markdown("<h1 style='margin-left: -20px;'>🧠 CEREBRO SISTEMA</h1>", unsafe_allow_html=True)
    
    st.write("---")

    # Solo las pestañas operativas
    tab1, tab2, tab3 = st.tabs(["📊 MERCADO", "📦 LOGÍSTICA", "💼 COMERCIAL"])

    with tab1:
        st.subheader("Inteligencia de Precios")
        archivo = st.file_uploader("Subir Inventario", type=['xlsx'], key="main_up")
        if archivo:
            df = pd.read_excel(archivo, dtype={'Material': str})
            st.dataframe(df.head(10), use_container_width=True)
            if st.button("PROCESAR ANÁLISIS"):
                with st.spinner("IA analizando datos..."):
                    resultados = procesar_lote_industrial(df)
                st.success("Completado")

    # Módulos informativos para el resto
    with tab2: st.info("Área de Optimización de Stock")
    with tab3: st.info("Área de Estrategia Comercial")

    # Sidebar
    st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/b/be/W%C3%BCrth_logo.svg", width=100)
    if st.sidebar.button("CERRAR SESIÓN"):
        st.session_state["autenticado"] = False
        st.rerun()
