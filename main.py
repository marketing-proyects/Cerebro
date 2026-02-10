import streamlit as st
import pandas as pd
from modules.auth_manager import gestionar_login
from modules.ai_engine import procesar_lote_industrial

st.set_page_config(page_title="CEREBRO - WÜRTH", page_icon="🧠", layout="wide")

# Estilos Generales Würth
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #FFFFFF; }
    h1, h2 { color: #ED1C24; margin-bottom: 0px; }
    
    /* Botones principales del sistema */
    div.stButton > button {
        background-color: #ED1C24 !important;
        color: white !important;
        border: 2px solid #ED1C24 !important;
        font-weight: bold !important;
    }
    
    /* Tabs personalizadas */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { color: #FFFFFF; }
    .stTabs [aria-selected="true"] { color: #ED1C24 !important; border-bottom-color: #ED1C24 !important; }
    </style>
    """, unsafe_allow_html=True)

if gestionar_login():
    # ENCABEZADO: Logo pequeño como detalle y Título
    col_logo, col_tit = st.columns([1, 10])
    with col_logo:
        st.image("https://upload.wikimedia.org/wikipedia/commons/b/be/W%C3%BCrth_logo.svg", width=80)
    with col_tit:
        st.markdown("<h1>🧠 CEREBRO SISTEMA</h1>", unsafe_allow_html=True)
    
    st.write("---")

    # Organización por Departamentos
    tab1, tab2, tab3 = st.tabs(["📊 MERCADO", "📦 LOGÍSTICA", "💼 COMERCIAL"])

    with tab1:
        st.subheader("Análisis de Precios")
        archivo = st.file_uploader("Cargar Inventario", type=['xlsx'], key="up_mercado")
        if archivo:
            df = pd.read_excel(archivo, dtype={'Material': str})
            st.dataframe(df.head(10), use_container_width=True)
            if st.button("INICIAR INVESTIGACIÓN ESTRATÉGICA"):
                with st.spinner("IA analizando competencia..."):
                    resultados = procesar_lote_industrial(df)
                st.success("Análisis completado")

    with tab2:
        st.subheader("Optimización de Inventario")
        st.info("Departamento de Logística: Gestión de stock para materiales Würth.")

    with tab3:
        st.subheader("Gestión Comercial")
        st.info("Departamento de Ventas: Seguimiento de márgenes y objetivos.")

    # Sidebar con logo y cierre de sesión
    st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/b/be/W%C3%BCrth_logo.svg", width=100)
    st.sidebar.write(f"**Sesión:** {st.session_state['username']}")
    if st.sidebar.button("CERRAR SESIÓN"):
        st.session_state["autenticado"] = False
        st.rerun()
