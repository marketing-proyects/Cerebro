import streamlit as st
import pandas as pd
from modules.auth_manager import gestionar_login
from modules.data_processor import cargar_archivo, validar_columnas
from modules.ai_engine import procesar_lista_productos

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Cerebro - Market Intel AI",
    page_icon="🧠",
    layout="wide"
)

# --- ESTILOS PERSONALIZADOS (Programación "Invisible") ---
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #ff4b4b;
        color: white;
    }
    </style>
    """, unsafe_allow_努力=True)

# --- LÓGICA DE AUTENTICACIÓN ---
autenticado, usuario = gestionar_login()

if autenticado:
    # --- BARRA LATERAL (SIDEBAR) ---
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1693/1693746.png", width=100)
    st.sidebar.title(f"Bienvenido, {usuario}")
    st.sidebar.markdown("---")
    st.sidebar.info("Este sistema utiliza IA para analizar precios en tiempo real y facilitar la toma de decisiones.")
    
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state["authenticator"].logout('main')
        st.rerun()

    # --- CUERPO PRINCIPAL ---
    st.title("🧠 Cerebro: Inteligencia de Precios")
    st.subheader("Optimiza tu estrategia de mercado con IA")
    
    # PASO 1: CARGA DE ARCHIVO
    st.write("### 1. Carga tu inventario")
    df_usuario = cargar_archivo()
    
    if df_usuario is not None:
        # Definimos de columnas necesarias para que el motor funcione
        columnas_req = ["SKU", "Producto", "Precio", "URL Competidor"]
        
        if validar_columnas(df_usuario, columnas_req):
            st.success("Estructura de Excel validada.")
            
            with st.expander("Ver vista previa de mis datos"):
                st.dataframe(df_usuario, use_container_width=True)

            # PASO 2: ACTIVACIÓN DEL MOTOR DE IA
            st.write("### 2. Ejecutar Análisis de Mercado")
            if st.button("🚀 Iniciar Escaneo Inteligente"):
                with st.status("Procesando links con IA...", expanded=True) as status:
                    st.write("Conectando con el motor de búsqueda...")
                    resultados = procesar_lista_productos(df_usuario)
                    status.update(label="Análisis completado", state="complete", expanded=False)
                
                # PASO 3: RESULTADOS Y DESCARGA
                st.write("### 3. Resultados Obtenidos")
                df_final = pd.DataFrame(resultados)
                
                # Mostrar métricas rápidas
                col1, col2, col3 = st.columns(3)
                col1.metric("Productos Analizados", len(df_final))
                col2.metric("Oportunidades de Mejora", len(df_final[df_final['Diferencia %'] < 0]))
                col3.metric("Promedio Market Gap", f"{df_final['Diferencia %'].mean():.2f}%")
                
                st.dataframe(df_final, use_container_width=True)

                # Botón de descarga para el usuario
                csv = df_final.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Descargar Reporte en Excel (CSV)",
                    data=csv,
                    file_name='analisis_mercado_cerebro.csv',
                    mime='text/csv',
                )

else:
    # Mensaje si no se ha logueado
    st.info("Por favor, ingresa tus credenciales en el formulario de la izquierda para acceder al panel.")
