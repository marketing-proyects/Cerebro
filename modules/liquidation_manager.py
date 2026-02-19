import streamlit as st
import pandas as pd
import datetime

def mostrar_modulo_liquidacion(df_vencimientos, df_stock):
    st.title("🚀 Liquidación Estratégica")
    st.info("Este módulo analiza productos con riesgo de vencimiento y Overstock para proponer acciones comerciales.")

    # --- LÓGICA DE FILTROS ---
    col1, col2 = st.columns(2)
    with col1:
        dias_corte = st.slider("Ver vencimientos en los próximos (días):", 30, 360, 90)
    
    # --- PROCESAMIENTO ---
    # Convertimos fecha de vencimiento a objeto datetime
    df_vencimientos['Vencimiento'] = pd.to_datetime(df_vencimientos['Vencimiento'])
    hoy = pd.to_datetime(datetime.date.today())
    
    # Filtramos por riesgo y fecha
    riesgo_alto = df_vencimientos[
        (df_vencimientos['Vencimiento'] <= hoy + pd.Timedelta(days=dias_corte)) | 
        (df_vencimientos['Riesgo'] == 'ALTO')
    ]

    st.subheader(f"⚠️ Productos en Riesgo Crítico ({len(riesgo_alto)} artículos)")
    st.dataframe(riesgo_alto[['Codigo', 'Descripcion', 'Vencimiento', 'Stock', 'Riesgo']])

    # --- INTEGRACIÓN CON IA (COPILOT / AZURE OPENAI) ---
    st.divider()
    st.subheader("🤖 Consultor de Estrategia (Copilot Intelligence)")
    
    pregunta_ia = st.text_area(
        "Instrucciones para la IA:",
        value=f"Analiza estos {len(riesgo_alto)} productos. Sugiere una estrategia de pack promocional para los que vencen antes de 60 días sin bajar el margen del PPP en más de un 15%."
    )

    if st.button("Generar Propuesta de Acciones"):
        # Aquí es donde conectaríamos con la API de Azure OpenAI (Copilot engine)
        st.warning("Conectando con el motor de IA de la empresa... (Requiere configuración de Azure)")
        
        # Simulación de respuesta de IA basada en tus datos
        st.markdown("""
        **Propuesta Sugerida:**
        1. **Pack 'Ahorro Freno':** El producto 90890 108 011 tiene stock excedente. Crear oferta de 3x2.
        2. **Acción Urgente:** El producto 90890 100 045 vence en menos de 10 días. Liquidación al costo para evitar pérdida total.
        """)
