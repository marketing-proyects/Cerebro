import streamlit as st
import pandas as pd
from io import BytesIO

def mostrar_fijacion_precios():
    st.header("💰 Módulo de Fijación de Precios")
    
    # 1. Sincronización Dinámica de Competencia
    if 'resultados_investigacion' in st.session_state:
        with st.expander("📥 Selección de Productos", expanded=True):
            df_invest = pd.DataFrame(st.session_state['resultados_investigacion'])
            
            # Mostramos los datos originales del Excel (Código y Descripción Corta)
            df_visual = df_invest[['Original (Würth)', 'ADN Identificado']].drop_duplicates()
            df_visual.columns = ['Código / Producto', 'Descripción Detectada']

            seleccion = st.dataframe(
                df_visual, use_container_width=True, hide_index=True,
                on_select="rerun", selection_mode="multi-row"
            )
            
            indices = seleccion.selection.rows
            if indices:
                codigos = df_visual.iloc[indices]['Código / Producto'].tolist()
                df_filtrado = df_invest[df_invest['Original (Würth)'].isin(codigos)]
                
                # Almacenamos datos clave para la inteligencia del módulo
                st.session_state['precios_mkt'] = pd.to_numeric(df_filtrado['P. Minorista'], errors='coerce').dropna().tolist()
                st.session_state['competidores_activos'] = df_filtrado['Competidor'].unique().tolist()
                st.session_state['nombres_seleccionados'] = codigos
            else:
                st.session_state['precios_mkt'] = []

    # Variables de Mercado Reactivas
    precios_ref = st.session_state.get('precios_mkt', [])
    competidores = st.session_state.get('competidores_activos', [])
    promedio_mkt = sum(precios_ref) / len(precios_ref) if precios_ref else 0

    st.divider()

    # 2. Entradas de Usuario (Actualización Instantánea)
    col_c, col_e = st.columns(2)
    with col_c:
        st.subheader("📦 Costos de Importación")
        c_fabrica = st.number_input("Costo de Fábrica (Origen)", min_value=0.0, step=0.01, value=5.00)
        g_import = st.number_input("Gastos Importación (%)", min_value=0.0, value=40.0)
        c_cif = c_fabrica * (1 + (g_import / 100))
        st.metric("Costo Unitario (CIF)", f"{c_cif:,.2f}")

    with col_e:
        st.subheader("📈 Simulación de Escenario")
        margen = st.slider("Margen de Utilidad Deseado (%)", 0, 100, 35)
        estrategia_sim = st.selectbox("Probar Estrategia:", ["Basado en costo", "Paridad de mercado", "Descreme", "Penetración"])
        iva = st.checkbox("Incluir IVA Uruguay (22%)", value=True)

    # 3. Motor de Cálculo Dinámico
    precio_neto = 0.0
    if estrategia_sim == "Basado en costo" or not precios_ref:
        precio_neto = c_cif / (1 - (margen / 100)) if margen < 100 else c_cif
    elif estrategia_sim == "Paridad de mercado": precio_neto = promedio_mkt
    elif estrategia_manual == "Descreme": precio_neto = max(precios_ref) * 1.10
    elif estrategia_manual == "Penetración": precio_neto = min(precios_ref) * 0.90

    precio_final = precio_neto * 1.22 if iva else precio_neto

    # 4. INTELIGENCIA DE POSICIONAMIENTO (Sugerencia Única)
    if precios_ref:
        st.subheader("🏁 Posicionamiento de Mercado")
        
        # Gráfico Reactivo con Colores Diferenciados y Propuesta al Final
        # Usamos st.bar_chart con una estructura que permita ver la propuesta destacada
        chart_data = pd.DataFrame({
            "Referencia": ["Suelo Competencia", "Medio Mercado", "Techo Competencia", "PROPUESTA WÜRTH"],
            "Precio": [min(precios_ref), promedio_mkt, max(precios_ref), precio_neto]
        }).set_index("Referencia")
        
        # Renderizado del gráfico (Streamlit colorea por columna si se estructura así)
        st.bar_chart(chart_data, color=["#1f77b4", "#1f77b4", "#1f77b4", "#FF0000"]) 

        # --- MOTOR DE SUGERENCIA ESTRATÉGICA ---
        dif_vs_mkt = ((precio_neto / promedio_mkt) - 1) * 100
        
        # Identificación dinámica de Tier basada en los competidores encontrados por la IA
        tier_alto = ["bosch", "makita", "dewalt", "milwaukee", "hilti", "stihl"]
        es_premium = any(t in str(competidores).lower() for t in tier_alto)

        st.info("💡 **Análisis del Cerebro:**")
        
        if es_premium:
            st.markdown(f"**Se sugiere Estrategia de Paridad.** Al detectarse competidores de alto desempeño ({', '.join(competidores[:3])}), Würth debe posicionarse como una alternativa técnica directa. Estás un {dif_vs_mkt:.1f}% respecto al promedio.")
        elif dif_vs_mkt < -15:
            st.markdown(f"**Se sugiere Estrategia de Ajuste de Margen.** Frente a la competencia actual, tu precio es significativamente bajo. Sugerimos subir el margen para capturar el valor de marca Würth y alinearse más al techo del mercado.")
        else:
            st.markdown(f"**Se sugiere Estrategia de Descreme.** Dado que los competidores detectados permiten un margen superior, sugerimos mantener un precio Premium para reforzar el posicionamiento de calidad superior de la marca.")

    # 5. Resultados y Exportación
    st.divider()
    r1, r2, r3 = st.columns(3)
    r1.metric("Costo CIF Final", f"{c_cif:,.2f}")
    r2.metric("PVP Final Sugerido", f"{precio_final:,.2f}")
    m_real = ((precio_neto - c_cif) / precio_neto * 100) if precio_neto > 0 else 0
    r3.metric("Margen Real Obtenido", f"{m_real:.1f}%")

    if st.button("📥 Exportar Análisis"):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            pd.DataFrame({
                "Parámetro": ["Productos Analizados", "Costo CIF", "Precio Final", "Margen %", "Competidores"],
                "Valor": [", ".join(st.session_state.get('nombres_seleccionados', [])), c_cif, precio_final, f"{m_real:.1f}%", ", ".join(competidores)]
            }).to_excel(writer, index=False)
        st.download_button("💾 Bajar Reporte", output.getvalue(), "Pricing_Final_Wuerth.xlsx")
