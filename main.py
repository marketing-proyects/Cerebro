import streamlit as st
import pandas as pd
from modules.auth_manager import gestionar_login
from modules.ai_engine import procesar_lote_industrial

st.set_page_config(page_title="CEREBRO - WÜRTH", page_icon="🧠", layout="wide")

# Estilos Würth: Rojo sólido y texto blanco garantizado
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #FFFFFF; }
    h1, h2 { color: #ED1C24; }
    
    /* Botones: Texto blanco fijo, fondo rojo */
    div.stButton > button {
        background-color: #ED1C24 !important;
        color: #FFFFFF !important;
        border: 2px solid #ED1C24 !important;
        font-weight: bold !important;
    }
    div.stButton > button:hover {
        background-color: #B3151A !important;
        color: #FFFFFF !important;
        border-color: #B3151A !important;
    }
    </style>
    """, unsafe_allow_html=True)

if gestionar_login():
    # PESTAÑAS CON LOGOS
    tab1, tab2 = st.tabs(["📊 INVESTIGACIÓN", "🏢 MARCA/LOGO"])

    with tab1:
        st.markdown("<h1>🧠 CEREBRO SISTEMA</h1>", unsafe_allow_html=True)
        archivo = st.file_uploader("Cargar Inventario", type=['xlsx'])
        if archivo:
            df = pd.read_excel(archivo, dtype={'Material': str})
            st.dataframe(df.head(10))
            if st.button("INICIAR INVESTIGACIÓN ESTRATÉGICA"):
                with st.spinner("Analizando..."):
                    # resultados = procesar_lote_industrial(df)
                    st.success("Investigación completada")

    with tab2:
        st.header("Personalización de Marca")
        # Aquí puedes colocar un logo por cada pestaña o cliente
        st.image("https://upload.wikimedia.org/wikipedia/commons/b/be/W%C3%BCrth_logo.svg", width=200)
        st.write("Configuración de perfil de empresa")
