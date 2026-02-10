import streamlit as st
import pandas as pd
from modules.auth_manager import gestionar_login
from modules.ai_engine import procesar_lote_industrial

# 1. Configuración de página
st.set_page_config(
    page_title="CEREBRO - WÜRTH", 
    page_icon="🧠", 
    layout="wide"
)

# 2. Estilos para Fondo Blanco y Botones Rojos
st.markdown("""
    <style>
    /* Fondo blanco y texto oscuro */
    .stApp { background-color: #FFFFFF; color: #333333; }
    
    /* Títulos en Rojo Würth */
    h1, h2, h3 { color: #ED1C24 !important; }
    
    /* Botones: Fondo Rojo, Texto Blanco */
    div.stButton > button {
        background-color: #ED1C24 !important;
        color: white !important;
        border: none !important;
        font-weight: bold !important;
    }
    /* Forzar visibilidad del texto en el botón */
    div.stButton > button p { color: white !important; }
    
    /* Pestañas personalizadas */
    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .stTabs [aria-selected="true"] { 
        color: #ED1C24 !important; 
        border-bottom-color: #ED1C24 !important; 
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Validación de Acceso (Sin st.write para evitar el "0")
if gestionar_login():
    
    # ENCABEZADO: Logo Detalle y Título
    col_l, col_t = st.columns([1, 10])
    with col_l:
        st.image("https://upload.wikimedia.org/wikipedia/commons/b/be/W%C3%BCrth_logo.svg", width=80)
    with col_t:
        st.markdown("<h1 style='margin-top: 10px;'>🧠 CEREBRO SISTEMA</h1>", unsafe_allow_html=True)
    
    st.divider()

    # 4. Pestañas de Departamentos (Eliminada la de Marca)
    tab1, tab2, tab3 = st.tabs(["📊 INTELIGENCIA DE MERCADO", "📦 LOGÍSTICA", "💼 COMERCIAL"])

    with tab1:
        st.subheader("Investigación de Precios y Competencia")
        st.write("Cargue su inventario para que la IA analice el mercado.")
        
        # Cargador de archivos (Mantiene los ceros a la izquierda de los códigos Würth)
        archivo = st.file_uploader("Subir Inventario (xlsx)", type=['xlsx'], key="main_up")
        
        if archivo:
            # Forzamos 'Material' a string para no perder el formato 089...
            df = pd.read_excel(archivo, dtype={'Material': str})
            
            st.write("### 🔍 Vista Previa")
            st.dataframe(df.head(10), use_container_width=True)
            
            if st.button("EJECUTAR ANÁLISIS ESTRATÉGICO"):
                with st.spinner("IA analizando competencia..."):
                    # Motor de IA para el SaaS de investigación
                    resultados = procesar_lote_industrial(df)
                
                st.success("ANÁLISIS COMPLETADO")
                df_final = pd.DataFrame(resultados)
                st.dataframe(df_final, use_container_width=True)
                
                st.download_button(
                    "DESCARGAR REPORTE CSV",
                    df_final.to_csv(index=False).encode('utf-8'),
                    "reporte_mercado.csv",
                    "text/csv"
                )

    with tab2:
        st.subheader("Gestión de Stock")
        st.info("Módulo de optimización logística.")

    with tab3:
        st.subheader("Estrategia Comercial")
        st.info("Módulo de análisis de ventas.")

    # 5. Barra Lateral
    st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/b/be/W%C3%BCrth_logo.svg", width=100)
    st.sidebar.write(f"**Usuario:** {st.session_state['username']}")
    
    if st.sidebar.button("CERRAR SESIÓN"):
        st.session_state["autenticado"] = False
        st.rerun()
