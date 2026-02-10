import streamlit as st
import pandas as pd
from modules.auth_manager import gestionar_login
from modules.ai_engine import procesar_lote_industrial

# Configuración de página
st.set_page_config(page_title="CEREBRO - MARKET RESEARCH - BY W-UY", page_icon="🧠", layout="wide")

# Estilos Futuristas
st.markdown("""
    <style>
    .stApp { background-color: #121417; color: #FFFFFF; }
    h1 { color: #00FBFF; text-shadow: 0px 0px 8px rgba(0, 251, 255, 0.2); }
    .stDataFrame { background-color: #1E2227; border-radius: 8px; }
    .stButton>button { border: 1px solid #00FBFF; color: #00FBFF; background: transparent; width: 100%; }
    .stButton>button:hover { box-shadow: 0px 0px 15px #00FBFF; color: #121417; background: #00FBFF; }
    </style>
    """, unsafe_allow_html=True)

# Validación de acceso
if gestionar_login():
    # Barra Lateral
    usuario = st.session_state.get("username", "Admin")
    st.sidebar.markdown(f"<h3 style='color: #00FBFF;'>⚙️ SESIÓN: {usuario}</h3>", unsafe_allow_html=True)
    
    if st.sidebar.button("CERRAR SESIÓN"):
        st.session_state["autenticado"] = False
        st.rerun()

    # Contenido Principal
    st.markdown("<h1>🧠 CEREBRO SISTEMA ⚙️</h1>", unsafe_allow_html=True)
    st.write("Investigación de Mercado Automática para Inventarios Técnicos")
    st.write("---")

    # Cargador de Archivos (Aquí subes el Excel de Würth corregido)
    archivo = st.file_uploader("Cargar Inventario (xlsx)", type=['xlsx'])
    
    if archivo:
        # Cargamos el DF asegurando que los códigos se lean como texto
        df = pd.read_excel(archivo, dtype={'Material': str})
        
        st.write("### 🔍 Vista Previa del Inventario")
        st.dataframe(df.head(10), use_container_width=True)
        
        if st.button("EJECUTAR INVESTIGACIÓN DE MERCADO"):
            with st.spinner("IA: Investigando competencia y precios en el mercado..."):
                # Llamada al motor de IA que ya tienes configurado
                resultados = procesar_lote_industrial(df)
            
            st.success("INVESTIGACIÓN FINALIZADA")
            df_final = pd.DataFrame(resultados)
            
            st.write("### 📊 Inteligencia de Mercado Consolidada")
            st.dataframe(df_final, use_container_width=True)
            
            # Botón de descarga del reporte final
            st.download_button(
                label="DESCARGAR REPORTE DE MERCADO",
                data=df_final.to_csv(index=False).encode('utf-8'),
                file_name="reporte_mercado_cerebro.csv",
                mime="text/csv"
            )
