import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

def mostrar_fijacion_precios():
    st.header("💰 Módulo de Fijación de Precios")
    
    # 1. Sincronización Dinámica (Código y Descripción Independientes)
    if 'resultados_investigacion' in st.session_state:
        with st.expander("📥 Selección de Productos", expanded=True):
            df_invest = pd.DataFrame(st.session_state['resultados_investigacion'])
            
            # Extraemos Código y Descripción de forma limpia
            df_visual = pd.DataFrame()
            df_visual['Código'] = df_invest['Original (Würth)'].astype(str).str.split().str[0]
            df_visual['Descripción'] = df_invest['Original (Würth)'].astype(str).str.split(n=1).str[1].str.split('\n').str[0]
            df_display = df_visual.drop_duplicates()

            seleccion = st.dataframe(
                df_display, use_container_width=True, hide_index=True,
                on_select="rerun", selection_mode="multi-row"
            )
            
            indices = seleccion.selection.rows
            if indices:
                codigos_sel = df_display.iloc[indices]['Código'].tolist()
                # Filtramos el origen para obtener datos de competencia y calidad
                st.session_state['df_mkt_actual'] = df_invest[df_invest['Original (Würth)'].astype(str).str.startswith(tuple(codigos_sel))]
                st.session_state['nombres_sel'] = df_display.iloc[indices]['Descripción'].tolist()

    df_mkt = st.session_state.get('df_mkt_actual', pd.DataFrame())
    st.divider()

    # 2. Variables Comerciales Reactivas
    col_c, col_e = st.columns(2)
    with col_c:
        st.subheader("📦 Costos de Importación")
        c_fabrica = st.number_input("Costo de Fábrica (Origen)", min_value=0.0, step=0.1, value=5.00)
        g_import = st.number_input("Gastos Importación (%)", min_value=0.0, step=0.1, value=40.0)
        c_cif = c_fabrica * (1 + (g_import / 100))
        st.metric("Costo Unitario (CIF)", f"{c_cif:,.2f}")

    with col_e:
        st.subheader("📈 Margen Deseado")
        margen_objetivo = st.slider("Margen de Utilidad (%)", 0, 100, 35)
        iva = st.checkbox("Incluir IVA Uruguay (22%)", value=True)

    # 3. Motor de Decisión Automático (Basado en Calidad detectada por IA)
    precio_base_neto = c_cif / (1 - (margen_objetivo / 100)) if margen_objetivo < 100 else c_cif
    
    if not df_mkt.empty:
        precios_ref = pd.to_numeric(df_mkt['P. Minorista'], errors='coerce').dropna().tolist()
        promedio_mkt = sum(precios_ref) / len(precios_ref)
        
        # Inteligencia Contextual: Leemos la calidad que la IA asignó a los competidores
        es_contra_premium = any(df_mkt['Calidad'].astype(str).str.contains('Premium|Líder|Alto', case=False, na=False))
        
        # Lógica de Posicionamiento
        estrategia_sug = "Basado en Costo"
        precio_final_neto = precio_base_neto
        dif_vs_mkt = ((precio_base_neto / promedio_mkt) - 1) * 100

        if es_contra_premium:
            estrategia_sug = "Paridad Competitiva"
            precio_final_neto = promedio_mkt
        elif dif_vs_mkt > 15: estrategia_sug = "Descreme"
        elif dif_vs_mkt < -15: estrategia_sug = "Penetración"

        p_final_con_iva = precio_final_neto * 1.22 if iva else precio_final_neto

        # 4. GRÁFICO DE DISPERSIÓN (Visualización de Posicionamiento)
        st.subheader(f"🏁 Sugerencia Estratégica: {estrategia_sug}")
        
        df_scatter = df_mkt[['Competidor', 'P. Minorista']].copy()
        df_scatter.columns = ['Vendedor', 'Precio']
        df_scatter['Precio'] = pd.to_numeric(df_scatter['Precio'], errors='coerce')
        df_scatter['Entidad'] = 'Competencia'
        
        # Añadimos a Würth en ROJO y más grande
        propuesta_row = pd.DataFrame({'Vendedor': ['PROPUESTA WÜRTH'], 'Precio': [precio_final_neto], 'Entidad': ['Würth']})
        df_scatter = pd.concat([df_scatter, propuesta_row], ignore_index=True)

        fig = px.scatter(
            df_scatter, x="Precio", y="Vendedor", color="Entidad",
            color_discrete_map={'Competencia': '#1f77b4', 'Würth': '#FF0000'},
            size=df_scatter['Entidad'].map({'Competencia': 10, 'Würth': 25}),
            title="Mapa de Posicionamiento: Würth vs Competencia Detectada"
        )
        
        # Líneas de referencia para Suelo, Techo y Medio
        fig.add_vline(x=min(precios_ref), line_dash="dash", line_color="gray", annotation_text="Suelo")
        fig.add_vline(x=max(precios_ref), line_dash="dash", line_color="gray", annotation_text="Techo")
        fig.add_vline(x=promedio_mkt, line_dash="dot", line_color="green", annotation_text="Precio Medio")
        
        fig.update_layout(showlegend=False, height=450)
        st.plotly_chart(fig, use_container_width=True)

        # Análisis Narrativo
        if es_contra_premium:
            st.info(f"**Análisis:** Se sugiere **{estrategia_sug}**. Al competir contra marcas Premium, Würth debe alinearse a estos valores para no quedar fuera de mercado por precio.")
        else:
            st.info(f"**Análisis:** Se sugiere **{estrategia_sug}**. Würth puede capitalizar su valor de marca por encima de los competidores estándar detectados.")

    # 5. Resultados y Exportación
    st.divider()
    r1, r2, r3 = st.columns(3)
    r1.metric("Costo CIF", f"{c_cif:,.2f}")
    r2.metric("PVP Final", f"{p_final_con_iva:,.2f}")
    m_real = ((precio_final_neto - c_cif) / precio_final_neto * 100) if precio_final_neto > 0 else 0
    r3.metric("Margen Real", f"{m_real:.1f}%")

    if st.button("📥 Exportar Análisis"):
        output = BytesIO()
        df_res = pd.DataFrame({
            "Parámetro": ["Productos", "CIF", "Precio Sugerido", "Margen %", "Estrategia"],
            "Valor": [", ".join(st.session_state.get('nombres_sel', [])), c_cif, p_final_con_iva, f"{m_real:.1f}%", estrategia_sug]
        })
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_res.to_excel(writer, index=False)
        st.download_button("💾 Bajar Excel", output.getvalue(), "Analisis_Estrategico_Wuerth.xlsx")
