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
            
            # Mostramos Código y Descripción Corta por separado
            df_visual = df_invest[['Original (Würth)', 'ADN Identificado']].drop_duplicates()
            df_visual.columns = ['Código / Producto', 'Descripción Detectada']

            seleccion = st.dataframe(
                df_visual, use_container_width=True, hide_index=True,
                on_select="rerun", selection_mode="multi-row"
            )
            
            indices = seleccion.selection.rows
            if indices:
                codigos = df_visual.iloc[indices]['Código / Producto'].tolist()
                # Filtramos el origen para obtener precios y calidades analizadas por la IA
                st.session_state['df_mkt_actual'] = df_invest[df_invest['Original (Würth)'].isin(codigos)]
                st.session_state['nombres_seleccionados'] = codigos

    df_mkt = st.session_state.get('df_mkt_actual', pd.DataFrame())
    st.divider()

    # 2. Variables Comerciales (Inputs Reactivos)
    col_c, col_e = st.columns(2)
    with col_c:
        st.subheader("📦 Costo de Importación")
        c_fabrica = st.number_input("Costo de Fábrica (Origen)", min_value=0.0, step=0.01, value=5.00)
        g_import = st.number_input("Gastos Importación (%)", min_value=0.0, value=40.0)
        c_cif = c_fabrica * (1 + (g_import / 100))
        st.metric("Costo CIF Final", f"{c_cif:,.2f}")

    with col_e:
        st.subheader("📈 Margen Deseado")
        margen_objetivo = st.slider("Margen de Utilidad Deseado (%)", 0, 100, 35)
        iva = st.checkbox("Incluir IVA Uruguay (22%)", value=True)

    # 3. MOTOR DE DECISIÓN DINÁMICO (Basado en Calidad IA)
    precio_base_neto = c_cif / (1 - (margen_objetivo / 100)) if margen_objetivo < 100 else c_cif
    
    if not df_mkt.empty:
        precios_ref = pd.to_numeric(df_mkt['P. Minorista'], errors='coerce').dropna().tolist()
        promedio_mkt = sum(precios_ref) / len(precios_ref)
        
        # --- INTELIGENCIA CONTEXTUAL ---
        # Leemos la columna 'Calidad' o 'Nivel' que generó la IA en la investigación
        # Buscamos si hay competidores marcados como 'Premium' o 'Líder'
        es_contra_premium = any(df_mkt['Calidad'].astype(str).str.contains('Premium|Líder|Alto', case=False, na=False))
        
        estrategia_sugerida = "Basado en Costo"
        precio_estrategico_neto = precio_base_neto
        dif_vs_mkt = ((precio_base_neto / promedio_mkt) - 1) * 100

        if es_contra_premium:
            # Si la IA detectó marcas Premium, la sugerencia es Paridad
            estrategia_sugerida = "Paridad Competitiva"
            precio_estrategico_neto = promedio_mkt
        elif dif_vs_mkt > 15:
            estrategia_sugerida = "Descreme"
        elif dif_vs_mkt < -15:
            estrategia_sugerida = "Penetración"

        precio_final = precio_estrategico_neto * 1.22 if iva else precio_estrategico_neto

        # 4. GRÁFICO DE DISPERSIÓN (Visualización de Posicionamiento)
        st.subheader(f"🏁 Sugerencia Estratégica: {estrategia_sugerida}")
        
        df_scatter = df_mkt[['Competidor', 'P. Minorista']].copy()
        df_scatter.columns = ['Entidad', 'Precio']
        df_scatter['Precio'] = pd.to_numeric(df_scatter['Precio'], errors='coerce')
        df_scatter['Tipo'] = 'Competencia'
        
        # Añadimos la propuesta de Würth destacada
        propuesta_row = pd.DataFrame({'Entidad': ['PROPUESTA WÜRTH'], 'Precio': [precio_estrategico_neto], 'Tipo': ['Würth']})
        df_scatter = pd.concat([df_scatter, propuesta_row], ignore_index=True)

        fig = px.scatter(
            df_scatter, x="Precio", y="Entidad", color="Tipo",
            color_discrete_map={'Competencia': '#1f77b4', 'Würth': '#FF0000'},
            size=[10] * (len(df_scatter)-1) + [22], # Würth destaca
            title="Posicionamiento Würth vs Mercado Detectado"
        )
        fig.update_layout(showlegend=False, height=450)
        st.plotly_chart(fig, use_container_width=True)

        # Explicación del "Por qué" basada en la Calidad detectada
        if es_premium:
            st.info(f"**Análisis:** Se sugiere **{estrategia_sugerida}**. La IA detectó competidores de nivel Premium en esta categoría. Würth debe alinearse a estos valores para competir por calidad y respaldo técnico.")
        else:
            st.info(f"**Análisis:** Se sugiere **{estrategia_sugerida}**. Dado que los competidores detectados son de un segmento inferior o estándar, Würth puede capitalizar su valor de marca con un posicionamiento superior.")

    # 5. Resultados y Reporte
    st.divider()
    r1, r2, r3 = st.columns(3)
    r1.metric("Costo CIF", f"{c_cif:,.2f}")
    r2.metric("PVP Final", f"{precio_final:,.2f}")
    m_real = ((precio_estrategico_neto - c_cif) / precio_estrategico_neto * 100) if precio_estrategico_neto > 0 else 0
    r3.metric("Margen Real", f"{m_real:.1f}%")

    if st.button("📥 Exportar Análisis"):
        output = BytesIO()
        df_res = pd.DataFrame({
            "Parámetro": ["Productos", "CIF", "Precio Final", "Margen %", "Estrategia"],
            "Valor": [", ".join(st.session_state.get('nombres_seleccionados', [])), c_cif, precio_final, f"{m_real:.1f}%", estrategia_sugerida]
        })
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_res.to_excel(writer, index=False)
        st.download_button("💾 Bajar Excel", output.getvalue(), "Estrategia_Wuerth.xlsx")
