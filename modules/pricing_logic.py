import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

def mostrar_fijacion_precios():
    st.header("💰 Módulo de Fijación de Precios")
    
    # 1. Selección de Productos (Respetando Columnas Independientes)
    if 'resultados_investigacion' in st.session_state:
        with st.expander("📥 Selección de Productos", expanded=True):
            df_invest = pd.DataFrame(st.session_state['resultados_investigacion'])
            
            # Limpieza para mostrar Código y Descripción por separado
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
                # Filtramos el origen para obtener precios y calidades detectadas por la IA
                st.session_state['df_mkt_actual'] = df_invest[df_invest['Original (Würth)'].astype(str).str.startswith(tuple(codigos_sel))]
                st.session_state['nombres_seleccionados'] = df_display.iloc[indices]['Descripción'].tolist()

    df_mkt = st.session_state.get('df_mkt_actual', pd.DataFrame())
    st.divider()

    # 2. Variables Comerciales Reactivas
    col_c, col_e = st.columns(2)
    with col_c:
        st.subheader("📦 Costo de Importación")
        c_fabrica = st.number_input("Costo de Fábrica (Origen)", min_value=0.0, step=0.1, value=5.00)
        g_import = st.number_input("Gastos Importación (%)", min_value=0.0, step=0.1, value=40.0)
        c_cif = c_fabrica * (1 + (g_import / 100))
        st.metric("Costo Unitario (CIF)", f"{c_cif:,.2f}")

    with col_e:
        st.subheader("📈 Margen Deseado")
        margen_objetivo = st.slider("Margen de Utilidad Deseado (%)", 0, 100, 35)
        iva = st.checkbox("Incluir IVA Uruguay (22%)", value=True)

    # --- INICIALIZACIÓN DE VARIABLES PARA EVITAR UNBOUNDLOCALERROR ---
    estrategia_sug = "Basado en Costo"
    precio_estrategico_neto = c_cif / (1 - (margen_objetivo / 100)) if margen_objetivo < 100 else c_cif
    es_contra_premium = False
    precios_ref = []

    # 3. Motor de Decisión Dinámico (Si hay datos de mercado)
    if not df_mkt.empty:
        precios_ref = pd.to_numeric(df_mkt['P. Minorista'], errors='coerce').dropna().tolist()
        if precios_ref:
            promedio_mkt = sum(precios_ref) / len(precios_ref)
            
            # Inteligencia Contextual de la IA
            es_contra_premium = any(df_mkt['Calidad'].astype(str).str.contains('Premium|Líder|Alto', case=False, na=False))
            
            dif_vs_mkt = ((precio_estrategico_neto / promedio_mkt) - 1) * 100

            if es_contra_premium:
                estrategia_sug = "Paridad Competitiva"
                precio_estrategico_neto = promedio_mkt
            elif dif_vs_mkt > 15: 
                estrategia_sug = "Descreme"
            elif dif_vs_mkt < -15: 
                estrategia_sug = "Penetración"

    p_final_con_iva = precio_estrategico_neto * 1.22 if iva else precio_estrategico_neto

    # 4. GRÁFICO DE DISPERSIÓN
    if not df_mkt.empty and precios_ref:
        st.subheader(f"🏁 Análisis Estratégico: {estrategia_sug}")
        
        df_scatter = df_mkt[['Competidor', 'P. Minorista']].copy()
        df_scatter.columns = ['Vendedor', 'Precio']
        df_scatter['Precio'] = pd.to_numeric(df_scatter['Precio'], errors='coerce')
        df_scatter['Entidad'] = 'Competencia'
        
        # Propuesta Würth en ROJO y destacada
        prop_row = pd.DataFrame({'Vendedor': ['PROPUESTA WÜRTH'], 'Precio': [precio_estrategico_neto], 'Entidad': ['Würth']})
        df_scatter = pd.concat([df_scatter, prop_row], ignore_index=True)

        fig = px.scatter(
            df_scatter, x="Precio", y="Vendedor", color="Entidad",
            color_discrete_map={'Competencia': '#1f77b4', 'Würth': '#FF0000'},
            size=df_scatter['Entidad'].map({'Competencia': 10, 'Würth': 25}),
            title="Mapa de Posicionamiento: Würth vs Competencia Detectada"
        )
        
        fig.add_vline(x=min(precios_ref), line_dash="dash", line_color="gray", annotation_text="Suelo")
        fig.add_vline(x=max(precios_ref), line_dash="dash", line_color="gray", annotation_text="Techo")
        fig.add_vline(x=sum(precios_ref)/len(precios_ref), line_dash="dot", line_color="green", annotation_text="Medio")
        
        fig.update_layout(showlegend=False, height=450)
        st.plotly_chart(fig, use_container_width=True)

        # Sugerencia Narrativa
        if es_contra_premium:
            st.info(f"**Se sugiere {estrategia_sug}.** Dado que compites contra marcas líderes, Würth debe alinearse a estos valores.")
        else:
            st.info(f"**Se sugiere {estrategia_sug}.** Puedes capitalizar el valor de marca superior de Würth frente a los competidores detectados.")

    # 5. RESULTADOS FINALES
    st.divider()
    r1, r2, r3 = st.columns(3)
    r1.metric("Costo CIF", f"{c_cif:,.2f}")
    r2.metric("PVP Final", f"{p_final_con_iva:,.2f}")
    m_real = ((precio_estrategico_neto - c_cif) / precio_estrategico_neto * 100) if precio_estrategico_neto > 0 else 0
    r3.metric("Margen Real", f"{m_real:.1f}%")

    if st.button("📥 Exportar Análisis"):
        output = BytesIO()
        df_res = pd.DataFrame({
            "Parámetro": ["Productos", "CIF", "Precio Sugerido", "Margen %", "Estrategia"],
            "Valor": [", ".join(st.session_state.get('nombres_seleccionados', [])), c_cif, p_final_con_iva, f"{m_real:.1f}%", estrategia_sug]
        })
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_res.to_excel(writer, index=False)
        st.download_button("💾 Bajar Excel", output.getvalue(), "Analisis_Estrategico_Wuerth.xlsx")
