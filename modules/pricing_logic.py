import streamlit as st
import pandas as pd
from io import BytesIO

def mostrar_fijacion_precios():
    st.header("💰 Módulo de Fijación de Precios")
    
    # 1. Sincronización de Productos (Mapeo directo Código/Descripción)
    if 'resultados_investigacion' in st.session_state:
        with st.expander("📥 Selección de Productos", expanded=True):
            df_invest = pd.DataFrame(st.session_state['resultados_investigacion'])
            
            # Tabla limpia para selección
            df_visual = df_invest[['Original (Würth)', 'ADN Identificado']].drop_duplicates()
            df_visual.columns = ['Código / Producto', 'Descripción Identificada']

            seleccion = st.dataframe(
                df_visual,
                use_container_width=True,
                hide_index=True,
                on_select="rerun",
                selection_mode="multi-row"
            )
            
            indices = seleccion.selection.rows
            if indices:
                codigos = df_visual.iloc[indices]['Código / Producto'].tolist()
                df_filtrado = df_invest[df_invest['Original (Würth)'].isin(codigos)]
                st.session_state['precios_mkt'] = pd.to_numeric(df_filtrado['P. Minorista'], errors='coerce').dropna().tolist()
                st.session_state['nombres_seleccionados'] = codigos
            else:
                st.session_state['precios_mkt'] = []

    precios_ref = st.session_state.get('precios_mkt', [])
    promedio_mkt = sum(precios_ref) / len(precios_ref) if precios_ref else 0

    st.divider()

    # 2. Entradas Reactivas (Costo y Margen)
    col_c, col_e = st.columns(2)
    with col_c:
        st.subheader("📦 Costo de Importación")
        c_fabrica = st.number_input("Costo de Fábrica (Origen)", min_value=0.0, step=0.01, value=5.00)
        g_import = st.number_input("Gastos de Importación/Aduana (%)", min_value=0.0, value=40.0)
        c_cif = c_fabrica * (1 + (g_import / 100))
        st.metric("Costo Unitario (CIF)", f"{c_cif:,.2f}")

    with col_e:
        st.subheader("📈 Margen y Estrategia")
        margen = st.slider("Margen de Utilidad Deseado (%)", 0, 100, 35)
        estrategia = st.selectbox("Estrategia Kotler", ["Basado en costo", "Paridad de mercado", "Descreme", "Penetración"])
        iva = st.checkbox("Incluir IVA Uruguay (22%)", value=True)

    # 3. Motor de Cálculo Dinámico
    precio_neto = 0.0
    if estrategia == "Basado en costo" or not precios_ref:
        precio_neto = c_cif / (1 - (margen / 100)) if margen < 100 else c_cif
    elif estrategia == "Paridad de mercado":
        precio_neto = promedio_mkt
    elif estrategia == "Descreme":
        precio_neto = max(precios_ref) * 1.10
    elif estrategia == "Penetración":
        precio_neto = min(precios_ref) * 0.90

    precio_final = precio_neto * 1.22 if iva else precio_neto
    m_real = ((precio_neto - c_cif) / precio_neto * 100) if precio_neto > 0 else 0

    # 4. Análisis de Posicionamiento y Sugerencia Técnica
    if precios_ref:
        st.subheader("🏁 Posicionamiento de Mercado")
        
        # Gráfico Reactivo con Títulos Claros
        chart_data = pd.DataFrame({
            "Referencia": ["Suelo Competencia", "Propuesta Würth", "Medio Mercado", "Techo Competencia"],
            "Precio": [min(precios_ref), precio_neto, promedio_mkt, max(precios_ref)]
        })
        st.bar_chart(chart_data, x="Referencia", y="Precio", color="#ff4b4b")

        # Lógica de Sugerencia con Explicación (Basada en tu solicitud)
        dif = ((precio_neto / promedio_mkt) - 1) * 100
        
        if dif > 15:
            st.error(f"**Se sugiere Estrategia de Descreme.**")
            st.info(f"Sugerimos esta opción porque tu precio está un {dif:.1f}% sobre el promedio. Es ideal para productos Premium con alta exclusividad o baja disponibilidad en el mercado local.")
        elif dif < -15:
            st.warning(f"**Se sugiere Estrategia de Penetración.**")
            st.info(f"Sugerimos esta opción porque estás un {abs(dif):.1f}% por debajo del promedio. Tienes una oportunidad agresiva para ganar cuota de mercado rápidamente o desplazar competidores.")
        else:
            st.success(f"**Se sugiere Estrategia de Paridad.**")
            st.info(f"Sugerimos esta opción porque estás alineado al mercado (Dif: {dif:.1f}%). Es el posicionamiento más equilibrado para mantener volumen sin sacrificar margen innecesariamente.")

    # 5. Resultados Finales y Exportación
    st.divider()
    res1, res2, res3 = st.columns(3)
    res1.metric("Costo CIF Final", f"{c_cif:,.2f}")
    res2.metric("PVP Sugerido", f"{precio_final:,.2f}")
    res3.metric("Margen Real", f"{m_real:.1f}%")

    if st.button("📥 Exportar Análisis"):
        output = BytesIO()
        df_res = pd.DataFrame({
            "Parámetro": ["Productos Seleccionados", "Costo CIF", "Estrategia", "Precio Sugerido", "Margen Real %"],
            "Valor": [", ".join(st.session_state.get('nombres_seleccionados', [])), c_cif, estrategia, precio_final, f"{m_real:.1f}%"]
        })
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_res.to_excel(writer, index=False)
        st.download_button("💾 Guardar Reporte", output.getvalue(), "Analisis_Estrategico_Wuerth.xlsx")
