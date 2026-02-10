import streamlit as st
import pandas as pd
from modules.auth_manager import gestionar_login
from modules.data_processor import cargar_archivo, validar_columnas
from modules.ai_engine import procesar_investigacion_industrial

# Configuración de página con icono de Cerebro
st.set_page_config(
    page_title="Cerebro - Inteligencia Industrial", 
    page_icon="🧠", 
    layout="wide"
)

# Estilos CSS: Futurista, Minimalista y con Alto Contraste
st.markdown("""
    <style>
    .stApp {
        background-color: #121417;
        color: #FFFFFF;
    }
    
    h1 {
        color: #00FBFF;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        text-transform: uppercase;
        letter-spacing: 2px;
        text-shadow: 0px 0px 8px rgba(0, 251, 255, 0.2);
    }
    
    .stButton>button {
        background-color: transparent;
        color: #00FBFF;
        border: 1px solid #00FBFF;
        border-radius: 4px;
        padding: 0.5rem 2rem;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background-color: #00FBFF;
        color: #121417;
        box-shadow: 0px 0px 15px rgba(0, 251, 255, 0.4);
    }

    .stDataFrame {
        background-color: #1E2227;
        border: 1px solid #30363D;
        border-radius: 8px;
        padding: 10px;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# Lógica de Autenticación
autenticado, usuario = gestionar_login()

if autenticado:
    # Barra Lateral
    st.sidebar.markdown(f"<h3 style='color: #00FBFF;'>⚙️ SESIÓN: {usuario}</h3>", unsafe_allow_html=True)
    st.sidebar.markdown("---")
    
    # Encabezado Principal con Cerebro y Tuerca
    st.markdown("<h1>🧠 CEREBRO_SISTEMA ⚙️</h1>", unsafe_allow_html=True)
    st.write("---")

    # Área de Trabajo
    col_carga, col_info = st.columns([1, 1])

    with col_carga:
        st.subheader("📥 Inyección de Datos")
        df_usuario = cargar_archivo()
    
    if df_usuario is not None:
        columnas_req = [
            "Nombre", "Especificación", "Material/Norma", 
            "UE 1", "UE 2", "UE 3", 
            "Precio Propio (Ref)", "URL Competidor"
        ]
        
        if validar_columnas(df_usuario, columnas_req):
            st.write("### 🔍 Vista Previa de Datos")
            st.dataframe(df_usuario, use_container_width=True)
            
            if st.button("EJECUTAR ANÁLISIS DE MERCADO"):
                with st.spinner("NÚCLEO IA: Analizando variables industriales..."):
                    resultados = procesar_investigacion_industrial(df_usuario)
                
                st.success("ANÁLISIS COMPLETADO")
                df_final = pd.DataFrame(resultados)

                for _, row in df_final.iterrows():
                    if row["Es Oferta"]:
                        st.warning(f"⚡ PROMO DETECTADA: {row['Producto']} - {row['Alerta']}")
                
                st.write("### 📊 Salida de Inteligencia")
                st.dataframe(df_final, use_container_width=True)

                csv = df_final.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="DESCARGAR REPORTE LOG",
                    data=csv,
                    file_name='reporte_cerebro.csv',
                    mime='text/csv',
                )

    if st.sidebar.button("FINALIZAR SESIÓN"):
        st.session_state["authenticator"].logout('main')
        st.rerun()
else:
    st.markdown("<h2 style='text-align: center; color: #00FBFF;'>ACCESO RESTRINGIDO</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Por favor, identifíquese para activar el sistema.</p>", unsafe_allow_html=True)
