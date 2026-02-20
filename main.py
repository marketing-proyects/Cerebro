import streamlit as st

# 1. CONFIGURACIÓN DE PÁGINA: Obligatoriamente antes de importar tus módulos
st.set_page_config(page_title="SISTEMA CEREBRO - WÜRTH", page_icon="👁️‍🗨️", layout="wide")

# 2. Importación de todos los módulos de la aplicación
from modules.auth_manager import gestionar_login
from modules.pricing_logic import mostrar_fijacion_precios
from modules.market_intel import mostrar_investigacion
from modules.liquidation_manager import mostrar_modulo_liquidation

# 3. Estilos visuales de Würth (Colores corporativos)
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #333333; }
    h1 { color: #ED1C24 !important; }
    div.stButton > button { background-color: #ED1C24 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# 4. Lógica de autenticación y navegación
if gestionar_login():
    # Título corregido con comillas simples por fuera y dobles por dentro
    st.sidebar.title('INTELIGENCIA DE MARKETING Y MERCADO "CEREBRO"')
    st.sidebar.write(f"Usuario: **{st.session_state.get('username', 'admin')}**")
    st.sidebar.divider()
    
    # Menú de navegación
    modulos_disponibles = ["Investigación de Mercado", "Fijación de Precios", "Liquidación"] ##### AQUI ACCESO A MODULOS #####
    modulos = st.session_state.get("permisos", modulos_disponibles)
    
    # Aseguramos que "Liquidación" esté disponible en la lista si el usuario tiene permisos
    seleccion = st.sidebar.radio("Navegación:", modulos)
    
    st.sidebar.divider()
    if st.sidebar.button("CERRAR SESIÓN"):
        st.session_state["autenticado"] = False
        st.rerun()

    # Enrutamiento a las pestañas correspondientes
    if seleccion == "Investigación de Mercado":
        mostrar_investigacion()
        
    elif seleccion == "Fijación de Precios":
        mostrar_fijacion_precios()

    elif seleccion == "Liquidación": ##### NUEVO #####
        mostrar_modulo_liquidation() ##### NUEVO #####
