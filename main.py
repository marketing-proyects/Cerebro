import streamlit as st
import pandas as pd
from modules.auth_manager import gestionar_login
from modules.ai_engine import procesar_lote_industrial

# 1. Configuración de página
st.set_page_config(
    page_title="CEREBRO - WÜRTH - MARKET INTEL", 
    page_icon="🧠", 
    layout="wide"
)

# 2. Estilos Globales (Rojo Würth y Texto Blanco Blindado)
st.markdown("""
    <style>
    /* Fondo oscuro profesional */
    .stApp { background-color: #000000; color: #FFFFFF; }
    
    /* Títulos en Rojo Würth */
    h1, h2, h3 { color: #ED1C24 !important; }
    
    /* BOTONES: Forzar texto blanco nítido */
    div.stButton > button {
        background-color: #ED1C24 !important;
        color: white !important;
        border: 2px solid #ED1C24 !important;
        font-weight: bold !important;
    }
    
    /* Parche para el texto invisible dentro del botón de Streamlit */
    div.stButton > button p {
        color: white !important;
    }

    div.stButton > button:hover {
        background-color: #B3151A !important;
        border-color: #B3151A !important;
    }

    /* Estilo para las Pestañas (Tabs) */
    .stTabs [data-baseweb="tab-list"] { gap: 15px; }
    .stTabs [data-baseweb="tab"] {
        color: #FFFFFF;
        font-weight: bold;
    }
    .stTabs [aria-selected="true"] { 
        color: #ED1C24 !important; 
        border-bottom-color: #ED1C24 !important; 
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Lógica de Autenticación
# Usamos el 'if' directo para evitar que se imprima un '0' o 'False' en pantalla
if gestionar_login():
    
    # ENCABEZADO: Logo (Detalle sutil) y Título
    col_logo, col_tit = st.columns([1, 12])
    with col_logo:
        # Aquí puedes usar tu PNG local o la URL oficial
        st.image("https://upload.wikimedia.org/wikipedia/commons/b/be/W%C3%BCrth_logo.svg", width=80)
    with col_tit:
        st.markdown("<h1 style='margin-left: -20px; margin-top: 10px;'>🧠 CEREBRO SISTEMA</h1>", unsafe_allow_html=True)
    
    st.write("---")

    # 4. Organización por Departamentos (Pestañas Operativas)
    tab1, tab2, tab3 = st.tabs(["📊 INTELIGENCIA DE MERCADO", "📦 LOGÍSTICA", "💼 COMERCIAL"])

    with tab1:
        st.subheader("Investigación de Precios y Competencia")
        st.write("Analice sus SKUs de Würth con soporte de Inteligencia Artificial.")
        
        # Cargador de archivos con preservación de ceros iniciales
        archivo = st.file_uploader("Subir Inventario (xlsx)", type=['xlsx'], key="main_uploader")
        
        if archivo:
            # Forzamos 'Material' a string para que el código 089... no pierda el cero
            df = pd.read_excel(archivo, dtype={'Material': str})
            
            st.write("### 🔍 Vista Previa del Inventario")
            st.dataframe(df.head(10), use_container_width=True)
            
            if st.button("EJECUTAR INVESTIGACIÓN ESTRATÉGICA"):
                with st.spinner("IA Cerebro: Traduciendo descripciones e investigando competencia..."):
                    # Llamada al motor de IA desarrollado en Python
                    resultados = procesar_lote_industrial(df)
                
                st.success("INVESTIGACIÓN FINALIZADA")
                df_final = pd.DataFrame(resultados)
                st.dataframe(df_final, use_container_width=True)
                
                st.download_button(
                    "DESCARGAR REPORTE CONSOLIDADO",
                    df_final.to_csv(index=False).encode('utf-8'),
                    "reporte_mercado_wurth.csv",
                    "text/csv"
                )

    with tab2:
        st.subheader("Optimización de Stock")
        st.info("Módulo en desarrollo para la gestión técnica de materiales.")

    with tab3:
        st.subheader("Estrategia Comercial")
        st.info("Módulo en desarrollo para el seguimiento de márgenes de venta.")

    # 5. Barra Lateral (Sidebar)
    st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/b/be/W%C3%BCrth_logo.svg", width=100)
    st.sidebar.markdown(f"**Usuario Activo:** {st.session_state.get('username', 'admin')}")
    
    if st.sidebar.button("CERRAR SESIÓN"):
        st.session_state["autenticado"] = False
        st.rerun()

else:
    # Si no está autenticado, el formulario se muestra a través de gestionar_login()
    pass
