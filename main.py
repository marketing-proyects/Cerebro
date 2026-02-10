import streamlit as st
import pandas as pd
from modules.auth_manager import gestionar_login
from modules.ai_engine import procesar_lote_industrial

st.set_page_config(page_title="CEREBRO - WÜRTH", page_icon="🧠", layout="wide")

# Estilos Clean Office
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #333333; }
    h1, h2 { color: #ED1C24 !important; }
    div.stButton > button { background-color: #ED1C24 !important; color: white !important; }
    div.stButton > button p { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# Lógica de validación
if gestionar_login():
    # Encabezado
    col_l, col_t = st.columns([1, 10])
    with col_l:
        st.image("https://upload.wikimedia.org/wikipedia/commons/b/be/W%C3%BCrth_logo.svg", width=80)
    with col_t:
        st.markdown("<h1 style='margin-top: 10px;'>🧠 CEREBRO SISTEMA</h1>", unsafe_allow_html=True)
    
    st.divider()

    # Módulo Único: Investigación de Mercado
    st.subheader("Investigación de Precios y Competencia")
    st.write("Analice sus códigos Würth (xlsx, xlsm) con Inteligencia Artificial.")
    
    # AJUSTE: Se agregó 'xlsm' a los formatos permitidos
    archivo = st.file_uploader("Subir Inventario", type=['xlsx', 'xlsm'], key="uploader_final")
    
    if archivo:
        # Forzamos lectura de 'Material' como string para preservar el cero inicial
        # El motor openpyxl maneja automáticamente archivos con macros
        df = pd.read_excel(archivo, dtype={'Material': str}, engine='openpyxl')
        
        st.write("### 🔍 Vista Previa de Datos Detectados")
        st.dataframe(df.head(10), use_container_width=True)
        
        if st.button("EJECUTAR INVESTIGACIÓN ESTRATÉGICA"):
            with st.spinner("La IA está analizando los códigos y descripciones..."):
                resultados = procesar_lote_industrial(df)
            
            st.success("INVESTIGACIÓN FINALIZADA")
            df_final = pd.DataFrame(resultados)
            st.dataframe(df_final, use_container_width=True)
            
            st.download_button(
                "DESCARGAR RESULTADOS",
                df_final.to_csv(index=False).encode('utf-8'),
                "reporte_cerebro_wurth.csv",
                "text/csv"
            )

    # Sidebar: Solo información esencial
    st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/b/be/W%C3%BCrth_logo.svg", width=100)
    st.sidebar.markdown(f"**Usuario:** {st.session_state.get('username', 'admin')}")
    if st.sidebar.button("CERRAR SESIÓN"):
        st.session_state["autenticado"] = False
        st.rerun()
