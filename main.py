import streamlit as st
import pandas as pd
from modules.auth_manager import gestionar_login
from modules.ai_engine import procesar_lote_industrial

st.set_page_config(page_title="CEREBRO - WÜRTH", page_icon="🧠", layout="wide")

# Estilo para fondo blanco y eliminar el '0'
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #333333; }
    h1 { color: #ED1C24 !important; }
    div.stButton > button { background-color: #ED1C24 !important; color: white !important; }
    div.stButton > button p { color: white !important; }
    /* Esconder cualquier rastro de widget vacío */
    .stVerticalBlock > div > div > label { display: none; }
    </style>
    """, unsafe_allow_html=True)

# Lógica de Login
if gestionar_login():
    # Sidebar minimalista
    st.sidebar.markdown(f"**Usuario:** {st.session_state.get('username', 'admin')}")
    
    st.markdown("<h1>🧠 CEREBRO SISTEMA</h1>", unsafe_allow_html=True)
    st.subheader("Investigación de Mercado Uruguay")
    st.write("---")

    archivo = st.file_uploader("Subir Inventario (.xlsx, .xlsm)", type=['xlsx', 'xlsm'], key="up_main_final")
    
    if archivo:
        # Cargamos el archivo manteniendo los ceros iniciales
        df = pd.read_excel(archivo, dtype=str, engine='openpyxl')
        
        # Mapeamos tus columnas (Nombre -> Material, Especificación -> Descripción)
        mapeo = {'Nombre': 'Material', 'Especificación': 'Descripción'}
        df = df.rename(columns=mapeo)
        
        st.write("### 🔍 Vista previa de productos detectados")
        st.dataframe(df.head(10), use_container_width=True)
        
        if st.button("BUSCAR COMPETENCIA"):
            with st.spinner("IA analizando descripciones técnicas..."):
                resultados = procesar_lote_industrial(df)
            
            if resultados:
                st.success("ANÁLISIS COMPLETADO")
                st.dataframe(pd.DataFrame(resultados), use_container_width=True)
            else:
                st.warning("No se encontraron resultados comerciales para estos términos.")

    if st.sidebar.button("CERRAR SESIÓN"):
        st.session_state["autenticado"] = False
        st.rerun()
