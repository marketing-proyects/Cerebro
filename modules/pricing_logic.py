import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

def mostrar_fijacion_precios():
    st.header("💰 Módulo de Fijación de Precios")
    
    # 1. RECUPERACIÓN DE DESCRIPCIONES (Fuerza Bruta)
    if 'resultados_investigacion' in st.session_state:
        with st.expander("📥 Selección de Productos", expanded=True):
            df_invest = pd.DataFrame(st.session_state['resultados_investigacion'])
            
            # Aseguramos que la columna sea tratada como texto para evitar errores
            df_invest['Original (Würth)'] = df_invest['Original (Würth)'].astype(str)

            def extraer_limpio(celda):
                # Separamos el código (primera palabra) del resto (descripción)
                partes = celda.split(' ', 1)
                cod = partes[0] if len(partes) > 0 else "S/C"
                desc = partes[1].split('\n')[0] if len(partes) > 1 else "Descripción no encontrada"
                return pd.Series([cod, desc])

            df_visual = df_invest['Original (Würth)'].apply(extraer_limpio)
            df_visual.columns = ['Código', 'Descripción']
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
                # Filtro por coincidencia parcial para vincular con precios
                st.session_state['df_mkt_actual'] = df_invest[df_invest['Original (Würth)'].str.contains('|'.join(codigos_sel), na=False)]
                st.session_state['nombres_seleccionados'] = df_display.iloc[indices]['Descripción'].tolist()

    df_mkt = st.session_state.get('df_mkt_actual', pd.DataFrame())
    st.divider()

    # 2. VARIABLES DE COSTO Y MARGEN
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

    # 3. LÓGICA DE PRECIO (Inicialización Segura)
    precio_propuesto_neto = c_cif / (1 - (margen_objetivo / 100)) if margen_objetivo < 100 else c_cif
    estrategia_sug = "Basado en Costo"
    precios_ref = []

    if not df_mkt.empty:
        precios_ref = pd.to_numeric(df_mkt['P. Minorista'], errors='coerce').dropna().tolist()
        if precios_ref:
            promedio_mkt = sum(precios_ref) / len(precios_ref)
            # Detección de nivel de competencia según IA
            es_premium = any(df_mkt['Calidad'].astype(str).str.contains('Premium|Líder|Alto', case=False, na=False))
            
            if es_premium:
                estrategia_sug = "Paridad Competitiva"
                precio_propuesto_neto = promedio_mkt # Forzar sugerencia por calidad
            elif (precio_propuesto_neto / promedio_mkt) > 1.15:
                estrategia_sug = "Descreme"
            elif (precio_propuesto_neto / promedio_mkt) < 0.85:
                estrategia_sug = "Penetración"
            else:
                estrategia_sug = "Paridad de Mercado"

    p_final_con_iva = precio_propuesto_neto * 1.22 if iva else precio_propuesto_neto

    # 4. MAPA DE POSICIONAMIENTO (Estilo Nube de Puntos Estratégico)
    if not df_mkt.empty and precios_ref:
        st.subheader(f"📊 Mapa de Posicionamiento: {estrategia_sug}")
        
        # Datos de Competencia
        df_scatter = df_mkt[['Competidor', 'P. Minorista']].copy()
        df_scatter.columns = ['Vendedor', 'Precio']
        df_scatter['Precio'] = pd.to_numeric(df_scatter['Precio'], errors='coerce')
        df_scatter['Marca'] = 'Competencia'
        
        # Punto Würth (Burbuja Roja Dominante)
        prop_row = pd.DataFrame({'Vendedor': ['WÜRTH (Propuesta)'], 'Precio': [precio_propuesto_neto], 'Marca': ['Würth']})
        df_scatter = pd.concat([df_scatter, prop_row], ignore_index=True)

        fig = px.scatter(
            df_scatter, x="Precio", y="Vendedor", color="Marca",
            size=df_scatter['Marca'].map({'Competencia': 12, 'Würth': 42}),
            color_discrete_map={'Competencia': '#3498db', 'Würth': '#e74c3c'},
            template="plotly_white"
        )
        
        # Líneas de referencia: Suelo, Techo y Media (Verde)
        fig.add_vline(x=min(precios_ref), line_dash="dash", line_color="#95a5a6", annotation_text="Suelo")
        fig.add_vline(x=max(precios_ref), line_dash="dash", line_color="#95a5a6", annotation_text="Techo")
        fig.add_vline(x=sum(precios_ref)/len(precios_ref), line_width=2, line_color="#2ecc71", annotation_text="Media Mercado")
        
        fig.update_layout(showlegend=False, height=500, margin=dict(l=10, r=10, t=50, b=10))
        st.plotly_chart(fig, use_container_width=True)

        st.info(f"💡 **Se sugiere {estrategia_sug}:** La burbuja roja marca la posición óptima de Würth frente al ecosistema detectado.")

    # 5. KPIs Y EXPORTACIÓN
    st.divider()
    r1, r2, r3 = st.columns(3)
    r1.metric("Costo CIF", f"{c_cif:,.2f}")
    r2.metric("PVP Final (IVA)", f"{p_final_con_iva:,.2f}")
    m_real = ((precio_propuesto_neto - c_cif) / precio_propuesto_neto * 100) if precio_propuesto_neto > 0 else 0
    r3.metric("Margen Real", f"{m_real:.1f}%")

    if st.button("📥 Exportar Análisis"):
        output = BytesIO()
        df_res = pd.DataFrame({
            "Dato": ["Productos", "Costo CIF", "Precio Sugerido", "Estrategia"],
            "Valor": [", ".join(st.session_state.get('nombres_seleccionados', [])), c_cif, p_final_con_iva, estrategia_sug]
        })
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_res.to_excel(writer, index=False)
        st.download_button("💾 Bajar Excel", output.getvalue(), "Estrategia_Wuerth.xlsx")
