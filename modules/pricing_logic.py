import streamlit as st
import pandas as pd
from io import BytesIO

def mostrar_fijacion_precios():
    st.header("💰 Módulo de Fijación de Precios")
    
    # --- BOTÓN DE REFRESCAR / NUEVA INVESTIGACIÓN ---
    with st.sidebar:
        st.divider()
        if st.button("🔄 Nueva Investigación (Refrescar)", use_container_width=True, type="primary"):
            # Limpiamos las variables de estado para permitir una carga limpia
            for key in ['resultados_investigacion', 'df_mkt_actual', 'precios_mkt', 'nombres_seleccionados']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

    # 1. VISOR DE RESULTADOS Y SELECCIÓN (Versión funcional original)
    if 'resultados_investigacion' in st.session_state and st.session_state['resultados_investigacion']:
        df_invest = pd.DataFrame(st.session_state['resultados_investigacion'])
        
        with st.expander("📊 Vista Previa de la Investigación", expanded=True):
            st.dataframe(df_invest, use_container_width=True, hide_index=True)
            
            st.subheader("📥 Selección de Productos")
            # Volvemos a la búsqueda directa de columnas que funcionaba
            col_id = next((c for c in df_invest.columns if "Original" in c or "Würth" in c), df_invest.columns[0])
            
            df_sel = pd.DataFrame()
            df_sel['Código'] = df_invest[col_id].astype(str).str.split().str[0]
            
            if 'ADN Identificado' in df_invest.columns:
                df_sel['Descripción'] = df_invest['ADN Identificado'].fillna("Sin ADN")
            else:
                df_sel['Descripción'] = df_invest[col_id].astype(str).str.split(n=1).str[1].str.split('\n').str[0]

            df_sel = df_sel.drop_duplicates()

            seleccion = st.dataframe(
                df_sel, use_container_width=True, hide_index=True,
                on_select="rerun", selection_mode="multi-row"
            )
            
            indices = seleccion.selection.rows
            if indices:
                codigos = df_sel.iloc[indices]['Código'].tolist()
                mask = df_invest[col_id].astype(str).str.startswith(tuple(codigos))
                st.session_state['df_mkt_actual'] = df_invest[mask]
                st.session_state['precios_mkt'] = pd.to_numeric(df_invest[mask]['P. Minorista'], errors='coerce').dropna().tolist()
                st.session_state['nombres_seleccionados'] = df_sel.iloc[indices]['Descripción'].tolist()
    else:
        st.info("ℹ️ Realiza una investigación de mercado para comenzar el análisis de precios.")

    precios_ref = st.session_state.get('precios_mkt', [])
    df_mkt = st.session_state.get('df_mkt_actual', pd.DataFrame())
    promedio_mkt = sum(precios_ref) / len(precios_ref) if precios_ref else 0

    st.divider()

    # 2. ENTRADAS REACTIVAS
    col_c, col_e = st.columns(2)
    with col_c:
        st.subheader("📦 Costo de Importación")
        c_fabrica = st.number_input("Costo de Fábrica (Origen)", min_value=0.0, step=0.01, value=5.00)
        g_import = st.number_input("Gastos Aduana (%)", min_value=0.0, value=40.0)
        c_cif = c_fabrica * (1 + (g_import / 100))
        st.metric("Costo Unitario (CIF)", f"{c_cif:,.2f}")

    with col_e:
        st.subheader("📈 Configuración de Venta")
        margen = st.slider("Margen de Utilidad Deseado (%)", 0, 100, 35)
        estrategia_manual = st.selectbox("Simular Estrategia Kotler", ["Basado en costo", "Paridad de mercado", "Descreme", "Penetración"])
        aplicar_iva = st.checkbox("Incluir IVA Uruguay (22%)", value=True)

    # 3. MOTOR DE CÁLCULO (Corrección margen 100%)
    divisor = (1 - (margen / 100)) if margen < 100 else 0.0001
    
    if estrategia_manual == "Basado en costo" or not precios_ref:
        precio_neto = c_cif / divisor
    elif estrategia_manual == "Paridad de mercado":
        precio_neto = promedio_mkt
    elif estrategia_manual == "Descreme":
        precio_neto = max(precios_ref) * 1.10 if precios_ref else c_cif / divisor
    elif estrategia_manual == "Penetración":
        precio_neto = min(precios_ref) * 0.90 if precios_ref else c_cif / divisor

    precio_final_con_impuestos = precio_neto * 1.22 if aplicar_iva else precio_neto

    # 4. ESTRATEGIA DE FIJACIÓN DE PRECIO SUGERIDA
    if not df_mkt.empty and precios_ref:
        st.subheader("🧠 Análisis del Sistema")
        es_premium = any(df_mkt['Calidad'].astype(str).str.contains('Premium|Líder|Alto', case=False, na=False))
        
        if es_premium:
            st.success("**Estrategia de fijación de precio sugerida: Paridad Competitiva (Segmento Premium)**")
            st.info("Se recomienda esta estrategia debido a la presencia de marcas líderes. Würth debe posicionarse igualando el precio de referencia para validar su calidad técnica superior.")
        elif (c_cif / promedio_mkt) < 0.5:
            st.warning("**Estrategia de fijación de precio sugerida: Penetración / Crecimiento Agresivo**")
            st.info("Su costo de importación es bajo frente al mercado. Tiene una ventaja excepcional para ganar cuota rápidamente.")
        else:
            st.info("**Estrategia de fijación de precio sugerida: Descreme Controlado**")
            st.info("Basado en la superioridad de marca de Würth, se sugiere un precio superior al promedio del mercado.")

    # 5. GRÁFICO DE BARRAS (Como estaba solicitado)
    if precios_ref:
        st.subheader("🏁 Análisis Comparativo")
        chart_data = pd.DataFrame({
            "Referencia": ["Suelo", "Propuesta Würth", "Medio", "Techo"],
            "Precio": [min(precios_ref), precio_neto, promedio_mkt, max(precios_ref)]
        })
        st.bar_chart(chart_data, x="Referencia", y="Precio", color="#ff4b4b")

    # 6. RESULTADOS FINALES
    st.divider()
    m_real = ((precio_neto - c_cif) / precio_neto * 100) if precio_neto > 0 else 0
    res1, res2, res3 = st.columns(3)
    res1.metric("Costo CIF Final", f"{c_cif:,.2f}")
    res2.metric("PVP Final (Inc. IVA)" if aplicar_iva else "PVP Final (Neto)", f"{precio_final_con_impuestos:,.2f}")
    res3.metric("Margen Real", f"{m_real:.1f}%")
