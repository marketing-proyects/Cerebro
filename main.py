import streamlit as st
import pandas as pd
from modules.auth_manager import gestionar_login
from modules.ai_engine import procesar_lote_industrial

st.set_page_config(page_title="CEREBRO - WÜRTH", page_icon="🧠", layout="wide")

# Estilos de trabajo (Sin logo en sidebar)
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #333333; }
    h1 { color: #ED1C24 !important; }
    div.stButton > button { background-color: #ED1C24 !important; color: white !important; }
    div.stButton > button p { color: white !important; }
    /* Estilo para mensajes de error/advertencia */
    .stAlert { border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

if gestionar_login():
    # El logo ya no aparece aquí ni en la sidebar
    st.sidebar.markdown(f"**Usuario Activo:** {st.session_state.get('username', 'admin')}")
    
    st.markdown("<h1>🧠 CEREBRO SISTEMA</h1>", unsafe_allow_html=True)
    st.subheader("Investigación de Mercado Inteligente (Búsqueda Combinada)")
    st.write("---")

    archivo = st.file_uploader("Subir Inventario (.xlsx, .xlsm)", type=['xlsx', 'xlsm'], key="main_final")
    
    if archivo:
        df = pd.read_excel(archivo, dtype=str, engine='openpyxl')
        
        # Mapeo flexible para asegurar que encuentre los datos
        mapeo = {'Nombre': 'Material', 'Especificación': 'Descripción'}
        df = df.rename(columns=mapeo)
        
        st.write("### 🔍 Vista Previa de Datos Detectados")
        st.dataframe(df.head(10), use_container_width=True)
        
        if st.button("INICIAR INVESTIGACIÓN ESTRATÉGICA"):
            with st.spinner("La IA está cruzando códigos y descripciones para encontrar competencia..."):
                resultados = procesar_lote_industrial(df)
            
            if resultados:
                st.success("INVESTIGACIÓN FINALIZADA")
                st.dataframe(pd.DataFrame(resultados), use_container_width=True)
            else:
                st.error("⚠️ No se encontraron coincidencias. La IA requiere que la columna 'Descripción' tenga palabras clave claras.")

    if st.sidebar.button("CERRAR SESIÓN"):
        st.session_state["autenticado"] = False
        st.rerun()
