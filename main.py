import streamlit as st
import pandas as pd
from modules.auth_manager import gestionar_login
from modules.data_processor import cargar_archivo
from modules.ai_engine import procesar_lote_industrial

st.set_page_config(page_title="CEREBRO - WÜRTH - MARKET INTEL", page_icon="🧠", layout="wide")

# Estilos Futuristas Minimalistas
st.markdown("""
    <style>
    .stApp { background-color: #121417; color: #FFFFFF; }
    h1 { color: #00FBFF; text-shadow: 0px 0px 8px rgba(0, 251, 255, 0.2); }
    .stDataFrame { background-color: #1E2227; border-radius: 8px; }
    .stButton>button { border: 1px solid #00FBFF; color: #00FBFF; background: transparent; width: 100%; }
    .stButton>button:hover { box-shadow: 0px 0px 15px #00FBFF; color: #121417; background: #00FBFF; }
    </style>
    """, unsafe_allow_html=True)

# --- CAMBIO CRÍTICO AQUÍ ---
# Llamamos a la función. Ella se encarga de mostrar el formulario.
gestionar_login()

# Verificamos el estado de autenticación desde el session_state
if st.session_state.get("authentication_status"):
    usuario = st.session_state.get("username")
    
    st.sidebar.markdown(f"<h3 style='color: #00FBFF;'>⚙️ SESIÓN: {usuario}</h3>", unsafe_allow_html=True)
    st.markdown("<h1>🧠 CEREBRO SISTEMA ⚙️</h1>", unsafe_allow_html=True)
    st.write("Investigación de Mercado Automática para Inventarios Técnicos")
    st.write("---")

    archivo = st.file_uploader("Cargar Inventario (Columnas: Material, Texto breve de material)", type=['xlsx'])
    
    if archivo:
        df = pd.read_excel(archivo)
        st.write("### 🔍 Vista Previa del Inventario")
        st.dataframe(df.head(10), use_container_width=True)
        
        if st.button("EJECUTAR INVESTIGACIÓN DE MERCADO"):
            with st.spinner("IA: Traduciendo descripciones técnicas e investigando competencia..."):
                resultados = procesar_lote_industrial(df)
            
            st.success("INVESTIGACIÓN FINALIZADA")
            df_final = pd.DataFrame(resultados)
            
            st.write("### 📊 Inteligencia de Mercado Consolidada")
            st.dataframe(df_final, use_container_width=True)
            
            st.download_button(
                "DESCARGAR REPORTE DE MERCADO",
                df_final.to_csv(index=False).encode('utf-8'),
                "reporte_mercado.csv",
                "text/csv"
            )

# Si no está autenticado, el formulario de login ya se mostró arriba
elif st.session_state.get("authentication_status") is False:
    st.error("Usuario o contraseña incorrectos")
else:
    st.markdown("<h2 style='text-align: center; color: #00FBFF;'>ACCESO RESTRINGIDO</h2>", unsafe_allow_html=True)
    st.info("Por favor, ingrese sus credenciales en el formulario.")
