import streamlit as st
import pandas as pd
from modules.auth_manager import gestionar_login
from modules.ai_engine import procesar_lote_industrial

st.set_page_config(page_title="CEREBRO - WÜRTH", page_icon="🧠", layout="wide")

# Estilo de trabajo limpio
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #333333; }
    h1 { color: #ED1C24 !important; }
    div.stButton > button { background-color: #ED1C24 !important; color: white !important; }
    div.stButton > button p { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

if gestionar_login():
    # Menú lateral limpio sin imágenes
    st.sidebar.markdown(f"**Sesión activa:** {st.session_state.get('username', 'admin')}")
    
    st.markdown("<h1>🧠 CEREBRO SISTEMA</h1>", unsafe_allow_html=True)
    st.subheader("Investigación Estratégica de Mercado")
    st.write("---")

    archivo = st.file_uploader("Subir archivo de prueba (.xlsx, .xlsm)", type=['xlsx', 'xlsm'], key="main_v11")
    
    if archivo:
        # Cargamos los datos asegurando que se lean como texto
        df = pd.read_excel(archivo, dtype=str, engine='openpyxl')
        
        # Mapeamos Nombre y Especificación (tus columnas del Excel)
        mapeo = {'Nombre': 'Material', 'Especificación': 'Descripción'}
        df = df.rename(columns=mapeo)
        
        st.write("### 🔍 Vista previa de productos")
        st.dataframe(df.head(10), use_container_width=True)
        
        if st.button("BUSCAR COMPETENCIA EN URUGUAY"):
            with st.spinner("IA analizando términos como 'Adhesivo' o 'Cianocrilato'..."):
                resultados = procesar_lote_industrial(df)
            
            if resultados:
                st.success("ANÁLISIS COMPLETADO")
                st.dataframe(pd.DataFrame(resultados), use_container_width=True)
            else:
                st.error("No se encontraron coincidencias. Revise los términos de descripción.")

    if st.sidebar.button("CERRAR SESIÓN"):
        st.session_state["autenticado"] = False
        st.rerun()
