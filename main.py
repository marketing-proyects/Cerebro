import streamlit as st
import pandas as pd
from modules.auth_manager import gestionar_login
from modules.ai_engine import procesar_lote_industrial

st.set_page_config(page_title="CEREBRO - WÜRTH", page_icon="🧠", layout="wide")

# Estilos de trabajo (Fondo blanco, sin logos que generen el '0')
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #333333; }
    h1 { color: #ED1C24 !important; }
    div.stButton > button { background-color: #ED1C24 !important; color: white !important; }
    div.stButton > button p { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# Validación de acceso
if gestionar_login():
    # Sidebar minimalista (Sin logo para evitar errores)
    st.sidebar.markdown(f"**Usuario Activo:** {st.session_state.get('username', 'admin')}")
    
    st.markdown("<h1>🧠 CEREBRO SISTEMA</h1>", unsafe_allow_html=True)
    st.subheader("Investigación de Mercado Inteligente")
    st.write("---")

    # Cargador de archivos habilitado para macros
    archivo = st.file_uploader("Subir Inventario (.xlsx, .xlsm)", type=['xlsx', 'xlsm'], key="main_final_v10")
    
    if archivo:
        # Leemos todo como texto para no perder ceros iniciales
        df = pd.read_excel(archivo, dtype=str, engine='openpyxl')
        
        # Mapeamos 'Nombre' y 'Especificación' a los nombres internos
        mapeo = {'Nombre': 'Material', 'Especificación': 'Descripción'}
        df = df.rename(columns=mapeo)
        
        st.write("### 🔍 Vista Previa de Datos Detectados")
        st.dataframe(df.head(10), use_container_width=True)
        
        if st.button("EJECUTAR INVESTIGACIÓN ESTRATÉGICA"):
            with st.spinner("La IA está buscando equivalentes en el mercado uruguayo..."):
                resultados = procesar_lote_industrial(df)
            
            if resultados:
                st.success("INVESTIGACIÓN FINALIZADA")
                st.dataframe(pd.DataFrame(resultados), use_container_width=True)
            else:
                st.error("⚠️ La IA no encontró coincidencias. Revise los términos de la columna 'Descripción'.")

    if st.sidebar.button("CERRAR SESIÓN"):
        st.session_state["autenticado"] = False
        st.rerun()
