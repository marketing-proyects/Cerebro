import streamlit as st
import pandas as pd
from io import BytesIO

def mostrar_fijacion_precios():
    st.header("💰 Módulo de Fijación de Precios")
    
    # 1. VISOR DE RESULTADOS Y SELECCIÓN
    if 'resultados_investigacion' in st.session_state:
        df_invest = pd.DataFrame(st.session_state['resultados_investigacion'])
        
        with st.expander("📊 Vista Previa de la Investigación", expanded=True):
            st.dataframe(df_invest, use_container_width=True, hide_index=True)
            
            st.subheader("📥 Selección de Productos")
            # Identificación flexible de columnas para evitar KeyErrors
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
                df_filtrado = df_invest[mask]
                
                st.session_state['df_mkt_actual'] = df_filtrado
                st.session_state['precios_mkt'] = pd.to_numeric(df_filtrado['P. Minorista'], errors='coerce').dropna().tolist()
                st.session_state['nombres_seleccionados'] = df_sel.iloc[indices]['Descripción'].tolist()

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
        iva = st.checkbox("Incluir IVA Uruguay (22%)", value=True)

    # 3. MOTOR DE CÁLCULO DINÁMICO (Corrección margen 100%)
    if estrategia_manual == "Basado en costo" or not precios_ref:
        # Si el margen es 100, el denominador sería 0. Usamos una pequeña diferencia para evitar el error.
        divisor = (1 - (margen / 100)) if margen < 100 else 0.0001
        precio_neto = c_cif / divisor
    elif estrategia_manual == "Paridad de mercado":
        precio_neto = promedio_mkt
    elif estrategia_manual == "Descreme":
        precio_neto = max(precios_ref) * 1.10 if precios_ref else c_cif
    elif estrategia_manual == "Penetración":
        precio_neto = min(precios_ref) * 0.90 if precios_ref else c_cif

    # 4. ESTRATEGIA SUGERIDA POR EL SISTEMA (IA Contextual)
    if not df_mkt.empty and precios_ref:
        st.subheader("🧠 Análisis del Sistema")
        
        es_premium = any(df_mkt['Calidad'].astype(str).str.contains('Premium|Líder|Alto', case=False, na=False))
        nombres_rivales = df_mkt['Competidor'].unique().tolist()
        
        if es_premium:
            st.success(f"**Estrategia de fijación de precio sugerida: Paridad Competitiva (Segmento Premium)**")
            st.info(f"Se recomienda esta estrategia debido a la presencia de marcas líderes como {', '.join(nombres_rivales[:2])}. Dado el alto estándar de calidad detectado en el nicho, Würth debe posicionarse igualando el precio de referencia de la competencia para validar su calidad técnica superior y capturar al cliente profesional que busca respaldo y durabilidad.")
        elif (c_cif / promedio_mkt) < 0.5:
            st.warning(f"**Estrategia de fijación de precio sugerida: Penetración / Crecimiento Agresivo**")
            st.info("Su costo de importación actual es significativamente bajo en comparación con el promedio del mercado detectado. Esto otorga una ventaja competitiva excepcional para desplazar a competidores de menor calidad mediante un precio disruptivo, permitiendo ganar cuota de mercado rápidamente sin sacrificar la rentabilidad operativa del producto.")
        else:
            st.info(f"**Estrategia de fijación de precio sugerida: Descreme Controlado**")
            st.info("Basado en la superioridad de marca de Würth frente a los competidores estándar identificados en la zona, el sistema sugiere capitalizar el valor percibido. Usted puede permitirse un precio entre un 10% y 15% superior al promedio, enfocándose en un segmento que valora la garantía oficial y el servicio postventa por encima del precio unitario.")

    # 5. GRÁFICO DE BARRAS COMPARATIVO
    if precios_ref:
        st.subheader("🏁 Análisis Comparativo")
        chart_data = pd.DataFrame({
            "Referencia": ["Suelo", "Propuesta Würth", "Medio", "Techo"],
            "Precio": [min(precios_ref), precio_neto, promedio_mkt, max(precios_ref)]
        })
        st.bar_chart(chart_data, x="Referencia", y="Precio", color="#ff4b4b")

    # 6. RESULTADOS FINALES
    st.divider()
    precio_final = precio_neto * 1.22 if iva else precio_neto
    m_real = ((precio_neto - c_cif) / precio_neto * 100) if precio_neto > 0 else 0

    res1, res2, res3 = st.columns(3)
    res1.metric("Costo CIF Final", f"{c_cif:,.2f}")
    res2.metric("PVP Final", f"{precio_final:,.2f}")
    res3.metric("Margen Real", f"{m_real:.1f}%")

    if st.button("📥 Exportar Informe Final"):
        output = BytesIO()
        df_res = pd.DataFrame({
            "Parámetro": ["Costo CIF", "Estrategia Simulada", "PVP Final", "Margen Real %"],
            "Valor": [c_cif, estrategia_manual, precio_final, f"{m_real:.1f}%"]
        })
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_res.to_excel(writer, index=False)
        st.download_button("💾 Guardar Reporte", output.getvalue(), "Estrategia_Wuerth.xlsx")
