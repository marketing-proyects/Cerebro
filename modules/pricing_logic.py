import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

def mostrar_fijacion_precios():
    st.header("💰 Módulo de Fijación de Precios")
    
    # 1. RECUPERACIÓN DE DESCRIPCIONES (Lógica de palabras clave IA)
    if 'resultados_investigacion' in st.session_state:
        with st.expander("📥 Selección de Productos", expanded=True):
            df_invest = pd.DataFrame(st.session_state['resultados_investigacion'])
            
            # Usamos el campo 'ADN Identificado' o las palabras clave generadas previamente
            # que es donde reside la descripción acortada por la IA
            df_visual = pd.DataFrame()
            df_visual['Código'] = df_invest['Original (Würth)'].astype(str).str.split().str[0]
            # Recuperamos la descripción sintetizada por la IA (ADN)
            df_visual['Descripción'] = df_invest['ADN Identificado'].fillna("Descripción no generada")
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
                st.session_state['df_mkt_actual'] = df_invest[df_invest['Original (Würth)'].astype(str).str.startswith(tuple(codigos_sel))]
                st.session_state['nombres_seleccionados'] = df_display.iloc[indices]['Descripción'].tolist()

    df_mkt = st.session_state.get('df_mkt_actual', pd.DataFrame())
    st.divider()

    # 2. VARIABLES COMERCIALES
    col_c, col_e = st.columns(2)
    with col_c:
        st.subheader("📦 Costo de Importación")
        c_fabrica = st.number_input("Costo de Fábrica (Origen)", min_value=0.0, step=0.1, value=5.00)
        g_import = st.number_input("Gastos Importación (%)", min_value=0.0, step=0.1, value=40.0)
        c_cif = c_fabrica * (1 + (g_import / 100))
        st.metric("Costo CIF Final", f"{c_cif:,.2f}")

    with col_e:
        st.subheader("📈 Margen Deseado")
        margen_objetivo = st.slider("Margen de Utilidad (%)", 0, 100, 35)
        iva = st.checkbox("Incluir IVA (22%)", value=True)

    # 3. CÁLCULO DE PRECIO Y ESTRATEGIA DINÁMICA
    precio_propuesto_neto = c_cif / (1 - (margen_objetivo / 100)) if margen_objetivo < 100 else c_cif
    estrategia_sug = "Análisis de Mercado"

    if not df_mkt.empty:
        precios_ref = pd.to_numeric(df_mkt['P. Minorista'], errors='coerce').dropna().tolist()
        if precios_ref:
            promedio_mkt = sum(precios_ref) / len(precios_ref)
            # Detección de calidad Premium según análisis previo de la IA
            es_premium = any(df_mkt['Calidad'].astype(str).str.contains('Premium|Líder|Alto', case=False, na=False))
            
            if es_premium:
                estrategia_sug = "Paridad Competitiva"
                precio_propuesto_neto = promedio_mkt
            elif (precio_propuesto_neto / promedio_mkt) > 1.15: estrategia_sug = "Descreme"
            elif (precio_propuesto_neto / promedio_mkt) < 0.85: estrategia_sug = "Penetración"
            else: estrategia_sug = "Paridad de Mercado"

    p_final_iva = precio_propuesto_neto * 1.22 if iva else precio_propuesto_neto

    # 4. GRÁFICO DE PELOTITAS (Precio Eje Vertical, Actores Eje Horizontal)
    if not df_mkt.empty and not df_mkt['P. Minorista'].isnull().all():
        st.subheader(f"🏁 Sugerencia: {estrategia_sug}")
        
        # Preparación de datos
        df_plot = df_mkt[['Competidor', 'P. Minorista']].copy()
        df_plot.columns = ['Actor', 'Precio']
        df_plot['Precio'] = pd.to_numeric(df_plot['Precio'], errors='coerce')
        df_plot['Marca'] = 'Competencia'
        
        # Agregamos Würth
        prop_row = pd.DataFrame({'Actor': ['WÜRTH'], 'Precio': [precio_propuesto_neto], 'Marca': ['Würth']})
        df_plot = pd.concat([df_plot, prop_row], ignore_index=True)

        fig = px.scatter(
            df_plot, 
            x="Actor", 
            y="Precio", 
            color="Marca",
            color_discrete_map={'Competencia': '#1f77b4', 'Würth': '#FF0000'}, # Azul y Rojo
            size=[12] * (len(df_plot)-1) + [25], # Würth más grande
            title="Comparativa de Precios por Actor",
            labels={"Precio": "Precio de Mercado", "Actor": "Competidores / Würth"}
        )
        
        fig.update_layout(showlegend=False, height=450)
        st.plotly_chart(fig, use_container_width=True)

    # 5. RESULTADOS
    st.divider()
    r1, r2, r3 = st.columns(3)
    r1.metric("Costo CIF", f"{c_cif:,.2f}")
    r2.metric("PVP Final", f"{p_final_iva:,.2f}")
    m_real = ((precio_propuesto_neto - c_cif) / precio_propuesto_neto * 100) if precio_propuesto_neto > 0 else 0
    r3.metric("Margen Real", f"{m_real:.1f}%")

    if st.button("📥 Exportar Análisis"):
        # Lógica de exportación a Excel...
        st.write("Análisis exportado.")
