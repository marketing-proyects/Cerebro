import streamlit as st
import pandas as pd
from modules.auth_manager import gestionar_login
from modules.data_processor import cargar_archivo, validar_columnas
from modules.ai_engine import procesar_investigacion_industrial

# 1. Configuración de página con el nuevo icono de Robot
st.set_page_config(
    page_title="Cerebro - Investigador", 
    page_icon="🤖", 
    layout="wide"
)

# 2. Estilos CSS para Interfaz Futurista y Minimalista
st.markdown("""
    <style>
    /* Fondo oscuro profundo y fuente limpia */
    .stApp {
        background-color: #0E1117;
        color: #E0E0E0;
    }
    
    /* Títulos con efecto neón sutil */
    h1 {
        color: #00FFC8;
        font-family: 'Courier New', Courier, monospace;
        text-transform: uppercase;
        letter-spacing: 3px;
        text-shadow: 0px 0px 10px rgba(0, 255, 200, 0.3);
    }
    
    /* Botones estilo "Cyberpunk" */
    .stButton>button {
        background-color: transparent;
        color: #00FFC8;
        border: 1px solid #00FFC8;
        border-radius: 2px;
        transition: all 0.3s ease;
        font-weight: bold;
    }
    
    .stButton>button:hover {
        background-color: #00FFC8;
        color: #0E1117;
        box-shadow: 0px 0px 15px #00FFC8;
    }

    /* Ocultar elementos innecesarios para minimalismo */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Contenedores de datos */
    .stDataFrame {
        border: 1px solid #1E2633;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Lógica de Autenticación
autenticado, usuario = gestionar_login()

if autenticado:
    # Sidebar Minimalista
    st.sidebar.markdown(f"<h3 style='color: #00FFC8;'>USER_ID: {usuario}</h3>", unsafe_allow_html=True)
    st.sidebar.markdown("---")
    
    # Cuerpo Principal
    st.markdown("<h1>CEREBRO_SYSTEM_v1.0</h1>", unsafe_allow_html=True)
    st.write("---")

    # 4. Flujo de Trabajo
    col_input, col_status = st.columns([1, 1])

    with col_input:
        st.subheader("📥 Data_Injection")
        df_usuario = cargar_archivo()
    
    if df_usuario is not None:
        columnas_req = [
            "Nombre", "Especificación", "Material/Norma", 
            "UE 1", "UE 2", "UE 3", 
            "Precio Propio (Ref)", "URL Competidor"
        ]
        
        if validar_columnas(df_usuario, columnas_req):
            st.write("### 🔍 Raw_Data_Preview")
            st.dataframe(df_usuario, use_container_width=True)
            
            if st.button("EXECUTE_MARKET_ANALYSIS"):
                with st.spinner("AI_CORE: Procesando variables industriales..."):
                    resultados = procesar_investigacion_industrial(df_usuario)
                
                st.success("ANALYSIS_COMPLETE")
                df_final = pd.DataFrame(resultados)

                # Alertas visuales minimalistas
                for _, row in df_final.iterrows():
                    if row["Es Oferta"]:
                        st.warning(f"⚡ PROMO_DETECTED: {row['Producto']} - {row['Alerta']}")
                
                st.write("### 📊 Intel_Output")
                st.dataframe(df_final, use_container_width=True)

                # Exportación
                csv = df_final.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="DOWNLOAD_REPORT_LOG",
                    data=csv,
                    file_name='cerebro_log.csv',
                    mime='text/csv',
                )

    if st.sidebar.button("TERMINATE_SESSION"):
        st.session_state["authenticator"].logout('main')
        st.rerun()
else:
    st.markdown("<h2 style='text-align: center; color: #00FFC8;'>ACCESS_RESTRICTED</h2>", unsafe_allow_html=True)
