import streamlit as st
import pandas as pd
from io import BytesIO

def mostrar_fijacion_precios():
    st.header("💰 Módulo de Fijación de Precios")
    
    # Inicialización de estados para reactividad
    if 'precios_mkt' not in st.session_state: st.session_state['precios_mkt'] = []
    
    # 1. Selección de Productos (Respetando Columnas de Excel)
    if 'resultados_investigacion' in st.session_state:
        with st.expander("📥 Selección de Productos", expanded=True):
            df_invest = pd.DataFrame(st.session_state['resultados_investigacion'])
            
            # Mostramos Código y Descripción de forma independiente
            df_visual = df_invest[['Original (Würth)', 'ADN Identificado']].drop_duplicates()
            df_visual.columns = ['Código / Producto', 'Descripción Corta']

            seleccion = st.dataframe(
                df_visual, use_container_width=True, hide_index=True,
                on_select="rerun", selection_mode="multi-row"
            )
            
            indices = seleccion.selection.rows
            if indices:
                codigos = df_visual.iloc[indices]['Código / Producto'].tolist()
                df_filtrado = df_invest[df_invest['Original (Würth)'].isin(codigos)]
                st.session_state['precios_mkt'] = pd.to_numeric(df_filtrado['P. Minorista'], errors='coerce').dropna().tolist()
                st.session_state['competidores_activos'] = df_filtrado['Competidor'].unique().tolist()
                st.session_state['nombres_seleccionados'] = codigos

    precios_ref = st.session_state.get('precios_mkt', [])
    competidores = st.session_state.get('competidores_activos', [])
    promedio_mkt = sum(precios_ref) / len(precios_ref) if precios_ref else 0

    st.divider()

    # 2. Variables Comerciales (Inputs Reactivos)
    col_c, col_e = st.columns(2)
    with col_c:
        st.subheader("📦 Costos de Importación")
        c_fabrica = st.number_input("Costo de Fábrica (Origen)", min_value=0.0, step=0.01, value=5.00)
        g_import = st.number_input("Gastos Importación (%)", min_value=0.0, value=40.0)
        c_cif = c_fabrica * (1 + (g_import / 100))
        st.metric("Costo CIF Final", f"{c_cif:,.2f}")

    with col_e:
        st.subheader("📈 Margen Deseado")
        margen_objetivo = st.slider("Margen de Utilidad (%)", 0, 100, 35)
        iva = st.checkbox("Incluir IVA Uruguay (22%)", value=True)

    # 3. MOTOR DE DECISIÓN AUTOMÁTICO (Sustituye al menú desplegable)
    # Calculamos primero el precio basado en el costo del usuario
    precio_base_neto = c_cif / (1 - (margen_objetivo / 100)) if margen_objetivo < 100 else c_cif
    
    # Identificación de Tier de Competencia
    tier_premium = ["bosch", "makita", "dewalt", "milwaukee", "hilti", "stihl"]
    es_contra_premium = any(t in str(competidores).lower() for t in tier_premium)
    
    estrategia_detectada = "Basado en Costo"
    precio_estrategico_neto = precio_base_neto

    if precios_ref:
        dif_vs_mkt = ((precio_base_neto / promedio_mkt) - 1) * 100
        
        if es_contra_premium:
            # Si hay marcas Pro, forzamos Paridad para no quedar fuera
            estrategia_detectada = "Paridad Competitiva"
            precio_estrategico_neto = promedio_mkt
        elif dif_vs_mkt > 15:
            estrategia_detectada = "Descreme"
            # Mantenemos el precio alto por la calidad Würth
            precio_estrategico_neto = precio_base_neto 
        elif dif_vs_mkt < -15:
            estrategia_detectada = "Penetración (Liderazgo en Costo)"
            precio_estrategico_neto = precio_base_neto

    precio_final = precio_estrategico_neto * 1.22 if iva else precio_estrategico_neto

    # 4. Visualización de Posicionamiento
    if precios_ref:
        st.subheader(f"🏁 Análisis Estratégico: {estrategia_detectada}")
        
        # Gráfico con la propuesta destacada en rojo al final
        chart_data = pd.DataFrame({
            "Referencia": ["Suelo Competencia", "Medio Mercado", "Techo Competencia", "PROPUESTA WÜRTH"],
            "Precio": [min(precios_ref), promedio_mkt, max(precios_ref), precio_estrategico_neto]
        }).set_index("Referencia")
        
        st.bar_chart(chart_data, color=["#1f77b4", "#1f77b4", "#1f77b4", "#FF0000"])

        # Explicación del "Por qué"
        st.info(f"**Sugerencia del Cerebro:** Se aplica **{estrategia_detectada}**. " + 
                (f"Al competir contra marcas como {', '.join(competidores[:2])}, el sistema prioriza el equilibrio de mercado." if es_contra_premium 
                 else "Dada la estructura de costos y la calidad de marca, este es el posicionamiento óptimo para maximizar rentabilidad."))

    # 5. Resultados y Exportación
    st.divider()
    r1, r2, r3 = st.columns(3)
    r1.metric("Costo CIF", f"{c_cif:,.2f}")
    r2.metric("PVP Final", f"{precio_final:,.2f}")
    m_real = ((precio_estrategico_neto - c_cif) / precio_estrategico_neto * 100) if precio_estrategico_neto > 0 else 0
    r3.metric("Margen Real", f"{m_real:.1f}%")

    if st.button("📥 Exportar Análisis"):
        output = BytesIO()
        df_res = pd.DataFrame({
            "Concepto": ["Productos", "Estrategia Detectada", "CIF", "PVP Final", "Margen Real"],
            "Valor": [", ".join(st.session_state.get('nombres_seleccionados', [])), estrategia_detectada, c_cif, precio_final, f"{m_real:.1f}%"]
        })
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_res.to_excel(writer, index=False)
        st.download_button("💾 Guardar Reporte", output.getvalue(), "Pricing_Wuerth_Auto.xlsx")
