import streamlit as st
import pandas as pd
from io import BytesIO

def mostrar_fijacion_precios():
    st.header("💰 Módulo de Fijación de Precios")
    
    # 1. Sincronización y Memoria de Competencia
    if 'resultados_investigacion' in st.session_state:
        with st.expander("📥 Selección de Productos", expanded=True):
            df_invest = pd.DataFrame(st.session_state['resultados_investigacion'])
            
            df_visual = df_invest[['Original (Würth)', 'ADN Identificado']].drop_duplicates()
            df_visual.columns = ['Código / Producto', 'Descripción']

            seleccion = st.dataframe(
                df_visual, use_container_width=True, hide_index=True,
                on_select="rerun", selection_mode="multi-row"
            )
            
            indices = seleccion.selection.rows
            if indices:
                codigos = df_visual.iloc[indices]['Código / Producto'].tolist()
                df_filtrado = df_invest[df_invest['Original (Würth)'].isin(codigos)]
                st.session_state['precios_mkt'] = pd.to_numeric(df_filtrado['P. Minorista'], errors='coerce').dropna().tolist()
                st.session_state['competidores_detectados'] = df_filtrado['Competidor'].unique().tolist()
                st.session_state['nombres_seleccionados'] = codigos
            else:
                st.session_state['precios_mkt'] = []

    precios_ref = st.session_state.get('precios_mkt', [])
    promedio_mkt = sum(precios_ref) / len(precios_ref) if precios_ref else 0
    competidores = st.session_state.get('competidores_detectados', [])

    st.divider()

    # 2. Entradas Reactivas
    col_c, col_e = st.columns(2)
    with col_c:
        st.subheader("📦 Costo de Importación")
        c_fabrica = st.number_input("Costo de Fábrica (Origen)", min_value=0.0, step=0.01, value=5.00)
        g_import = st.number_input("Gastos Importación (%)", min_value=0.0, value=40.0)
        c_cif = c_fabrica * (1 + (g_import / 100))
        st.metric("Costo CIF Final", f"{c_cif:,.2f}")

    with col_e:
        st.subheader("📈 Simulación de Escenario")
        margen_simulado = st.slider("Margen de Utilidad (%)", 0, 100, 35)
        estrategia_manual = st.selectbox("Probar Estrategia:", ["Basado en costo", "Paridad de mercado", "Descreme", "Penetración"])
        iva = st.checkbox("Incluir IVA (22%)", value=True)

    # 3. Cálculos Dinámicos
    precio_neto_sim = 0.0
    if estrategia_manual == "Basado en costo" or not precios_ref:
        precio_neto_sim = c_cif / (1 - (margen_simulado / 100)) if margen_simulado < 100 else c_cif
    elif estrategia_manual == "Paridad de mercado": precio_neto_sim = promedio_mkt
    elif estrategia_manual == "Descreme": precio_neto_sim = max(precios_ref) * 1.10
    elif estrategia_manual == "Penetración": precio_neto_sim = min(precios_ref) * 0.90

    precio_final = precio_neto_sim * 1.22 if iva else precio_neto_sim

    # 4. MOTOR DE SUGERENCIA ÚNICA (EL ASESOR)
    if precios_ref:
        st.subheader("🧠 Sugerencia Estratégica del Cerebro")
        
        # Lógica de detección de Tier de competencia
        tier_1 = ["bosch", "makita", "dewalt", "milwaukee", "hilti"]
        es_tier_alto = any(t in str(competidores).lower() for t in tier_1)
        
        dif_vs_mkt = ((precio_neto_sim / promedio_mkt) - 1) * 100

        # Bloque de Sugerencia Única
        if es_tier_alto:
            st.info("🎯 **Estrategia Sugerida: Paridad Competitiva**")
            st.write("Se sugiere esta estrategia porque compites contra marcas líderes (Bosch/Makita). Würth debe posicionarse cerca de estos valores para ser una alternativa válida por servicio y confianza, sin alejarse demasiado en precio.")
        elif dif_vs_mkt < -10:
            st.success("🎯 **Estrategia Sugerida: Ajuste de Margen al Alza**")
            st.write(f"Se sugiere subir el margen. Estás un {abs(dif_vs_mkt):.1f}% por debajo de marcas de menor segmento (como Total/Ingco). Würth tiene margen para capturar más valor manteniendo la competitividad.")
        else:
            st.error("🎯 **Estrategia Sugerida: Descreme Moderado**")
            st.write("Se sugiere esta estrategia. Dada la calidad Premium de Würth frente a la competencia detectada, puedes permitirte un precio superior al promedio.")

        # Gráfico de Posicionamiento
        chart_data = pd.DataFrame({
            "Referencia": ["Suelo Competencia", "Propuesta Würth", "Medio Mercado", "Techo Competencia"],
            "Precio": [min(precios_ref), precio_neto_sim, promedio_mkt, max(precios_ref)]
        })
        st.bar_chart(chart_data, x="Referencia", y="Precio", color="#ff4b4b")

    # 5. Cierre y Exportación
    st.divider()
    r1, r2, r3 = st.columns(3)
    r1.metric("Costo CIF", f"{c_cif:,.2f}")
    r2.metric("PVP Sugerido", f"{precio_final:,.2f}")
    m_real = ((precio_neto_sim - c_cif) / precio_neto_sim * 100) if precio_neto_sim > 0 else 0
    res3 = r3.metric("Margen Real", f"{m_real:.1f}%")

    if st.button("📥 Exportar Análisis"):
        # Lógica de exportación...
        st.write("Reporte generado con éxito.")
