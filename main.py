import streamlit as st
import pandas as pd
from modules.auth_manager import gestionar_login
from modules.ai_engine import procesar_lote_industrial

# Configuración base
st.set_page_config(page_title="CEREBRO - WÜRTH", page_icon="🧠", layout="wide")

# Estilos Clean Office
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
    # LUGAR RÍGIDO PARA EL LOGO: Sidebar
    st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/b/be/W%C3%BCrth_logo.svg", width=120)
    st.sidebar.divider()
    st.sidebar.markdown(f"**Usuario:** {st.session_state.get('username', 'admin')}")
    
    # Cuerpo Principal
    st.markdown("<h1>🧠 CEREBRO SISTEMA</h1>", unsafe_allow_html=True)
    st.subheader("Investigación de Mercado Automática")
    st.write("---")

    # Cargador de archivos (Soporta .xlsm)
    archivo = st.file_uploader("Subir Inventario (.xlsx, .xlsm)", type=['xlsx', 'xlsm'], key="main_up")
    
    if archivo:
        # dtype=str mantiene los ceros iniciales 0893... sin necesidad de comas o tildes
        df = pd.read_excel(archivo, dtype=str, engine='openpyxl')
        
        # MAPEO DE TUS COLUMNAS: Ajustamos Nombre y Especificación a lo que la IA entiende
        mapeo = {'Nombre': 'Material', 'Especificación': 'Descripción'}
        df = df.rename(columns=mapeo)
        
        st.write("### 🔍 Vista Previa de Datos")
        st.dataframe(df.head(10), use_container_width=True)
        
        if st.button("INICIAR INVESTIGACIÓN CON IA"):
            with st.spinner("La IA está investigando la competencia en Uruguay..."):
                resultados = procesar_lote_industrial(df)
            
            if resultados:
                st.success("INVESTIGACIÓN FINALIZADA")
                st.dataframe(pd.DataFrame(resultados), use_container_width=True)
            else:
                st.warning("No se encontraron resultados. Verifique los códigos del Excel.")

    if st.sidebar.button("CERRAR SESIÓN"):
        st.session_state["autenticado"] = False
        st.rerun()
