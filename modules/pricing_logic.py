import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

def mostrar_fijacion_precios():
    st.header("💰 Módulo de Fijación de Precios")
    
    # Inicialización de estados de sesión para mantener la fluidez
    if 'precios_mkt' not in st.session_state: st.session_state['precios_mkt'] = []
    if 'df_mkt_actual' not in st.session_state: st.session_state['df_mkt_actual'] = pd.DataFrame()
    if 'nombres_sel' not in st.session_state: st.session_state['nombres_sel'] = []

    # 1. Selección de Productos (Columnas Independientes)
    if 'resultados_investigacion' in st.session_state:
        with st.expander("📥 Selección de Productos del Inventario", expanded=True):
            df_invest = pd.DataFrame(st.session_state['resultados_investigacion'])
            
            # Procesamos las columnas para que Código y Descripción sean campos separados
            def extraer_codigo(x):
                s = str(x).strip()
                return s.split(' ')[0] if ' ' in s else s
            
            def extraer_desc(x):
                s = str(x).strip()
                # Tomamos solo la primera línea para evitar el análisis largo de la IA
                linea_uno = s.split('\n')[0]
                return linea_uno.split(' ', 1)[1] if ' ' in linea_uno else "Sin descripción"

            df_visual = pd.DataFrame()
            df_visual['Código'] = df_invest['Original (Würth)'].apply(extraer_codigo)
            df_visual['Descripción'] = df_invest['Original (Würth)'].apply(extraer_desc)
            df_display = df_visual.drop_duplicates()

            seleccion = st.dataframe(
                df_display, 
                use_container_width=True, 
                hide_index=True,
                on_select="rerun", 
                selection_mode="multi-row"
            )
            
            indices = seleccion.selection.rows
            if indices:
                codigos_sel = df_display.iloc[indices]['Código'].tolist()
                # Filtramos el origen para el motor de precios
                mask = df_invest['Original (Würth)'].astype(str).apply(lambda x: any(x.startswith(c) for c in codigos_sel))
                df_filtrado = df_invest[mask]
                
                st.session_state['df_mkt_actual'] = df_filtrado
                st.session_state['nombres_sel'] = df_display.iloc[indices]['Descripción'].tolist()
                st.session_state['precios_mkt'] = pd.to_numeric(df_filtrado['P. Minorista'], errors='coerce').dropna().tolist()

    df_mkt = st.session_state.get('df_mkt_actual', pd.DataFrame())
    precios_ref = st.session_state.get('precios_mkt', [])
    promedio_mkt = sum(precios_ref) / len(precios_ref) if precios_ref else 0
    
    st.divider()

    # 2. Variables Comerciales (Inputs Reactivos)
    col_c, col_e = st.columns(2)
    with col_c:
        st.subheader("📦 Costos de Importación")
        c_fabrica = st.number_input("Costo de Fábrica (Origen)", min_value=0.0, step=0.1, value=5.00)
        g_import = st.number_input("Gastos Importación (%)", min_value=0.0, step=0.1, value=40.0)
        c_cif = c_fabrica * (1 + (g_import / 100))
        st.metric("Costo Unitario (CIF)", f"{c_cif:,.2f}")

    with col_e:
        st.subheader("📈 Margen Deseado")
        margen_objetivo = st.slider("Margen de Utilidad Deseado (%)", 0, 100, 35)
        iva = st.checkbox("Incluir IVA Uruguay (22%)", value=True)

    # 3. Motor de Decisión Automático y Sugerencia Única
    precio_base_neto = c_cif / (1 - (margen_objetivo / 100)) if margen_objetivo < 100 else c_cif
    
    if not df_mkt.empty and precios_ref:
        # Inteligencia Contextual: Nivel de competencia detectado dinámicamente por la IA
        es_contra_premium = any(df_mkt['Calidad'].astype(str).str.contains('Premium|Líder|Alto', case=False, na=False)) if 'Calidad' in df_mkt.columns else False
        
        dif_vs_mkt = ((precio_base_neto / promedio_mkt) - 1) * 100
        
        # Lógica de Sugerencia
        if es_contra_premium:
            if abs(dif_vs_mkt) <= 15:
                sug_nombre, sug_tipo, sug_msg = "Paridad Competitiva", "success", "Se sugiere esta estrategia porque compites contra marcas líderes. Würth debe posicionarse cerca de estos valores para ser una alternativa válida por respaldo técnico, sin alejarse demasiado en precio."
            elif dif_vs_mkt > 15:
                sug_nombre, sug_tipo, sug_msg = "Descreme", "error", "Se sugiere esta estrategia. Tu precio es superior al promedio de marcas líderes. Es válido si el producto tiene una innovación única, pero monitorea si la rotación se mantiene."
            else:
                sug_nombre, sug_tipo, sug_msg = "Penetración Técnica", "warning", "Se sugiere esta estrategia. Estás por debajo de los líderes; tienes una oportunidad agresiva para desplazar a la competencia Premium con un precio más competitivo."
        else:
            # Competencia estándar/económica (Total, Ingco, etc.)
            if dif_vs_mkt > 10:
                sug_nombre, sug_tipo, sug_msg = "Descreme", "error", "Se sugiere esta estrategia. Dado que la competencia detectada es de segmento estándar, Würth debe capitalizar su valor de marca con un precio superior que refleje su mayor durabilidad."
            else:
                sug_nombre, sug_tipo, sug_msg = "Paridad de Mercado", "success", "Se sugiere esta estrategia. Estás alineado al promedio de marcas generales. Es el posicionamiento más seguro para ganar volumen sin entrar en guerras de precios."

        st.subheader(f"🧠 Sugerencia del Cerebro: {sug_nombre}")
        if sug_tipo == "success": st.success(sug_msg)
        elif sug_tipo == "warning": st.warning(sug_msg)
        else: st.error(sug_msg)

        # 4. Gráfico de Dispersión (Visualización de Posicionamiento)
        df_scatter = df_mkt[['Competidor', 'P. Minorista']].copy()
        df_scatter.columns = ['Vendedor', 'Precio']
        df_scatter['Precio'] = pd.to_numeric(df_scatter['Precio'], errors='coerce')
        df_scatter['Entidad'] = 'Competencia'
        
        # Propuesta Würth destacada
        prop_row = pd.DataFrame({'Vendedor': ['PROPUESTA WÜRTH'], 'Precio': [precio_base_neto], 'Entidad': ['Würth']})
        df_scatter = pd.concat([df_scatter, prop_row], ignore_index=True)

        fig = px.scatter(
            df_scatter, x="Precio", y="Vendedor", color="Entidad",
            color_discrete_map={'Competencia': '#1f77b4', 'Würth': '#FF0000'},
            size=df_scatter['Entidad'].map({'Competencia': 10, 'Würth': 22}),
            title="Posicionamiento Würth vs Mercado Detectado",
            labels={"Precio": "Precio Unitario (Neto)"}
        )
        # Líneas de referencia con la terminología solicitada
        fig.add_vline(x=min(precios_ref), line_dash="dash", line_color="blue", annotation_text="Suelo Competencia")
        fig.add_vline(x=max(precios_ref), line_dash="dash", line_color="blue", annotation_text="Techo Competencia")
        fig.add_vline(x=promedio_mkt, line_dash="dot", line_color="green", annotation_text="Precio Medio Mercado")
        
        fig.update_layout(showlegend=False, height=450)
        st.plotly_chart(fig, use_container_width=True)

    # 5. Resultados y Exportación
    st.divider()
    p_final = precio_base_neto * 1.22 if iva else precio_base_neto
    m_real = ((precio_base_neto - c_cif) / precio_base_neto * 100) if precio_base_neto > 0 else 0

    r1, r2, r3 = st.columns(3)
    r1.metric("Costo CIF Final", f"{c_cif:,.2f}")
    r2.metric("PVP Final Sugerido", f"{p_final:,.2f}")
    r3.metric("Margen Real Obtenido", f"{m_real:.1f}%")

    if st.button("📥 Exportar Análisis"):
        output = BytesIO()
        df_exp = pd.DataFrame({
            "Parámetro": ["Productos", "Costo CIF", "Precio Sugerido (Neto)", "PVP Final", "Margen %", "Estrategia"],
            "Valor": [", ".join(st.session_state.get('nombres_sel', [])), c_cif, precio_base_neto, p_final, f"{m_real:.1f}%", sug_nombre if 'sug_nombre' in locals() else "N/A"]
        })
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_exp.to_excel(writer, index=False)
        st.download_button("💾 Bajar Excel", output.getvalue(), "Analisis_Estrategico_Wuerth.xlsx")
