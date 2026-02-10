import streamlit as st
import pandas as pd
from modules.auth_manager import gestionar_login
from modules.ai_engine import procesar_lote_industrial

st.set_page_config(page_title="CEREBRO - WÜRTH", page_icon="🧠", layout="wide")

# Estilos Würth: Rojo y Negro con botones corregidos
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #FFFFFF; }
    h1, h2, h3 { color: #ED1C24; }
    
    /* Botones de acción: Rojo sólido, texto blanco */
    div.stButton > button {
        background-color: #ED1C24 !important;
        color: #FFFFFF !important;
        border: 2px solid #ED1C24 !important;
        font-weight: bold !important;
    }
    div.stButton > button:hover {
        background-color: #B3151A !important;
        border-color: #B3151A !important;
    }

    /* Pestañas */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        color: #FFFFFF;
        padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] { 
        color: #ED1C24 !important; 
        border-bottom-color: #ED1C24 !important;
    }
    </style>
    """, unsafe_allow_html=True)

if gestionar_login():
    # ENCABEZADO CON LOGO PEQUEÑO (DETALLE)
    col_logo, col_vacio = st.columns([1, 8])
    with col_logo:
        st.image("https://upload.wikimedia.org/wikipedia/commons/b/be/W%C3%BCrth_logo.svg", width=100)
    
    st.markdown("<h1>🧠 CEREBRO SISTEMA</h1>", unsafe_allow_html=True)
    st.write("Inteligencia Estratégica Multi-Departamento")
    st.write("---")

    # Navegación por departamentos (Sin pestaña de Marca)
    tab1, tab2, tab3 = st.tabs(["📊 INTELIGENCIA DE MERCADO", "📦 LOGÍSTICA", "💼 COMERCIAL"])

    with tab1:
        st.subheader("Análisis de Precios y Competencia")
        archivo = st.file_uploader("Cargar Inventario", type=['xlsx'], key="market_up")
        if archivo:
            df = pd.read_excel(archivo, dtype={'Material': str})
            st.dataframe(df.head(10), use_container_width=True)
            if st.button("EJECUTAR ANÁLISIS DE MERCADO"):
                with st.spinner("Procesando datos de Würth..."):
                    resultados = procesar_lote_industrial(df)
                st.success("Análisis finalizado")

    with tab2:
        st.subheader("Gestión de Stock y SKUs")
        st.info("Módulo de optimización para materiales técnicos.")

    with tab3:
        st.subheader("Estrategia de Ventas")
        st.info("Módulo de seguimiento de objetivos comerciales.")

    # Sidebar para sesión
    st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/b/be/W%C3%BCrth_logo.svg", width=80)
    st.sidebar.write(f"**Usuario:** {st.session_state['username']}")
    if st.sidebar.button("CERRAR SESIÓN"):
        st.session_state["autenticado"] = False
        st.rerun()
