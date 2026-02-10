import streamlit as st
import pandas as pd
from modules.auth_manager import gestionar_login
from modules.ai_engine import procesar_lote_industrial

st.set_page_config(page_title="CEREBRO - WÜRTH", page_icon="🧠", layout="wide")

# Estilos corregidos
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #333333; }
    h1 { color: #ED1C24 !important; }
    div.stButton > button { background-color: #ED1C24 !important; color: white !important; }
    div.stButton > button p { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# LLAMADA LIMPIA: Eliminamos cualquier rastro que genere el "0"
if gestionar_login():
    st.image("https://upload.wikimedia.org/wikipedia/commons/b/be/W%C3%BCrth_logo.svg", width=100)
    st.title("🧠 CEREBRO SISTEMA")
    st.divider()

    st.subheader("Investigación de Precios y Competencia")
    archivo = st.file_uploader("Subir Inventario", type=['xlsx', 'xlsm'], key="uploader_v4")
    
    if archivo:
        # Leemos el archivo asegurando que nada se convierta a número (mantiene ceros)
        df = pd.read_excel(archivo, dtype=str, engine='openpyxl')
        
        # MAPEO AUTOMÁTICO: Si tus columnas se llaman distinto, las renombramos para la IA
        mapeo = {'Nombre': 'Material', 'Especificación': 'Descripción'}
        df = df.rename(columns=mapeo)
        
        st.write("### 🔍 Vista Previa de Datos Detectados")
        st.dataframe(df.head(10), use_container_width=True)
        
        if st.button("EJECUTAR INVESTIGACIÓN ESTRATÉGICA"):
            with st.spinner("IA analizando datos..."):
                # Ahora la IA recibirá las columnas 'Material' y 'Descripción' que necesita
                resultados = procesar_lote_industrial(df)
            
            if resultados:
                st.success("INVESTIGACIÓN FINALIZADA")
                df_final = pd.DataFrame(resultados)
                st.dataframe(df_final, use_container_width=True)
            else:
                st.warning("⚠️ La IA no encontró coincidencias. Verifique que los códigos sean correctos.")

    # Sidebar sin el "0"
    st.sidebar.markdown(f"**Sesión:** {st.session_state.get('username', 'admin')}")
    if st.sidebar.button("CERRAR SESIÓN"):
        st.session_state["autenticado"] = False
        st.rerun()
