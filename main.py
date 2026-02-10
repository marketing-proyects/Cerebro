import streamlit as st
from modules.auth_manager import gestionar_login

st.set_page_config(page_title="CEREBRO - WÜRTH", page_icon="🧠", layout="wide")

# LLAMADA CORRECTA:
# Si pones st.write(gestionar_login()) o algo similar, aparecerá el "0".
if gestionar_login():
    # El resto de tu código solo se ejecuta si el login es exitoso
    st.markdown("<h1 style='color: #ED1C24;'>🧠 CEREBRO SISTEMA</h1>", unsafe_allow_html=True)

# Estilos Limpios (Fondo Blanco)
st.markdown("""
    <style>
    /* Fondo y texto base */
    .stApp { background-color: #FFFFFF; color: #333333; }
    
    /* Encabezados en Rojo */
    h1, h2, h3 { color: #ED1C24 !important; }
    
    /* Botones: Rojo sólido con texto blanco */
    div.stButton > button {
        background-color: #ED1C24 !important;
        color: white !important;
        border: 1px solid #ED1C24 !important;
        font-weight: bold !important;
    }
    div.stButton > button p { color: white !important; }
    
    /* Tabs (Pestañas) */
    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .stTabs [aria-selected="true"] { color: #ED1C24 !important; border-bottom-color: #ED1C24 !important; }
    </style>
    """, unsafe_allow_html=True)

if gestionar_login():
    # Encabezado con Logo
    col_l, col_t = st.columns([1, 10])
    with col_l:
        st.image("https://upload.wikimedia.org/wikipedia/commons/b/be/W%C3%BCrth_logo.svg", width=80)
    with col_t:
        st.markdown("<h1 style='margin-top: 10px;'>🧠 CEREBRO SISTEMA</h1>", unsafe_allow_html=True)
    
    st.divider()

    # Pestañas Departamentales
    tab1, tab2, tab3 = st.tabs(["📊 INTELIGENCIA DE MERCADO", "📦 LOGÍSTICA", "💼 COMERCIAL"])

    with tab1:
        st.subheader("Investigación de Precios y Competencia")
        archivo = st.file_uploader("Subir Inventario Würth (xlsx)", type=['xlsx'])
        
        if archivo:
            # Forzamos lectura de códigos de material como texto
            df = pd.read_excel(archivo, dtype={'Material': str})
            st.write("### 🔍 Vista Previa")
            st.dataframe(df.head(10), use_container_width=True)
            
            if st.button("EJECUTAR ANÁLISIS ESTRATÉGICO"):
                with st.spinner("La IA está analizando los códigos de Würth..."):
                    resultados = procesar_lote_industrial(df)
                st.success("Análisis completado con éxito")
                df_final = pd.DataFrame(resultados)
                st.dataframe(df_final, use_container_width=True)

    with tab2:
        st.subheader("Optimización de Stock")
        st.info("Módulo para gestión técnica de materiales.")

    with tab3:
        st.subheader("Estrategia Comercial")
        st.info("Módulo para análisis de márgenes de venta.")

    # Sidebar
    st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/b/be/W%C3%BCrth_logo.svg", width=100)
    st.sidebar.markdown(f"**Usuario:** {st.session_state['username']}")
    if st.sidebar.button("CERRAR SESIÓN"):
        st.session_state["autenticado"] = False
        st.rerun()
