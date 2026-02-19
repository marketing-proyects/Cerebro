import streamlit as st
import pandas as pd
from io import BytesIO

def mostrar_fijacion_precios():
    st.header("💰 Módulo de Fijación de Precios")
    
    # 1. VERIFICACIÓN Y VISOR DE RESULTADOS
    # Forzamos la detección de datos en la sesión
    if 'resultados_investigacion' in st.session_state and st.session_state['resultados_investigacion']:
        df_invest = pd.DataFrame(st.session_state['resultados_investigacion'])
        
        with st.expander("📊 Vista Previa de la Investigación", expanded=True):
            # Restauramos el preview para confirmar que los datos existen
            st.dataframe(df_invest, use_container_width=True, hide_index=True)
            
            st.subheader("📥 Selección de Productos")
            # Identificación flexible de columnas
            col_id = next((c for c in df_invest.columns if "Original" in c or "Würth" in c), df_invest.columns[0])
            
            df_sel = pd.DataFrame()
            df_sel['Código'] = df_invest[col_id].astype(str).str.split().str[0]
            
            # Recuperamos ADN o Fallback
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

    df_mkt = st.session_state.get('df_mkt_actual', pd.DataFrame())
    precios_ref = st.session_state.get('precios_mkt', [])
    promedio_mkt = sum(precios_ref) / len(precios_ref) if precios_ref else 0

    st.divider()

    # 2. ENTRADAS REACTIVAS
    col_c, col_e = st.columns(2)
    with col_c:
        st.subheader("📦 Costo de Importación")
        c_fabrica = st.number_input("Costo de Fábrica (Origen)", min_value=0.0, step=0.01, value=5.00)
        g_import = st.number_input("Gastos Aduana (%)", min_value=0.0, value=40.0)
        c_cif = c_fabrica * (1 + (g_import / 100))
        st.metric("Costo CIF", f"{c_cif:,.2f}")

    with col_e:
        st.subheader("📈 Simulación")
        margen = st.slider("Margen de Utilidad Deseado (%)", 0, 100, 35)
        estrategia_manual = st.selectbox("Estrategia Kotler", ["Basado en costo", "Paridad de mercado", "Descreme", "Penetración"])
        iva = st.checkbox("Incluir IVA (22%)", value=True)

    # 3. MOTOR DE CÁLCULO
    if estrategia_manual == "Basado en costo" or not precios_ref:
        precio_neto = c_cif / (1 - (margen / 100)) if margen < 100 else c_cif
    elif estrategia_manual == "Paridad de mercado":
        precio_neto = promedio_mkt
    elif estrategia_manual == "Descreme":
        precio_neto = max(precios_ref) * 1.10 if precios_ref else c_cif
    elif estrategia_manual == "Penetración":
        precio_neto = min(precios_ref) * 0.90 if precios_ref else c_cif

    # 4. SUGERENCIA ÚNICA INTELIGENTE
    if not df_mkt.empty and precios_ref:
        st.subheader("🧠 Sugerencia Estratégica")
        
        es_premium = any(df_mkt['Calidad'].astype(str).str.contains('Premium|Líder|Alto', case=False, na=False))
        if es_premium:
            st.success("**Veredicto: Paridad Competitiva.** Presencia de marcas líderes detectada. Mantener precio de mercado para validar calidad.")
        elif (precio_neto / promedio_mkt) < 0.80:
            st.warning("**Veredicto: Penetración.** Gran oportunidad de desplazar competencia estándar por costo.")
        else:
            st.info("**Veredicto: Descreme.** Capitalizar valor de marca Würth frente a competidores genéricos.")

    # 5. GRÁFICO DE BARRAS
    if precios_ref:
        st.subheader("🏁 Análisis Comparativo")
        chart_data = pd.DataFrame({
            "Referencia": ["Suelo", "Würth", "Medio", "Techo"],
            "Precio": [min(precios_ref), precio_neto, promedio_mkt, max(precios_ref)]
        })
        st.bar_chart(chart_data, x="Referencia", y="Precio", color="#ff4b4b")

    # 6. RESULTADOS
    st.divider()
    p_final = precio_neto * 1.22 if iva else precio_neto
    m_real = ((precio_neto - c_cif) / precio_neto * 100) if precio_neto > 0 else 0

    r1, r2, r3 = st.columns(3)
    r1.metric("CIF Final", f"{c_cif:,.2f}")
    r2.metric("PVP Final", f"{p_final:,.2f}")
    r3.metric("Margen Real", f"{m_real:.1f}%")
