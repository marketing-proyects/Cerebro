import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

def mostrar_fijacion_precios():
    st.header("💰 Módulo de Fijación de Precios")
    
    # 1. Selección de Productos (Mapeo Inteligente)
    if 'resultados_investigacion' in st.session_state:
        with st.expander("📥 Selección de Productos", expanded=True):
            df_invest = pd.DataFrame(st.session_state['resultados_investigacion'])
            
            # Limpieza de Código y Descripción
            df_visual = pd.DataFrame()
            df_visual['Código'] = df_invest['Original (Würth)'].astype(str).apply(lambda x: x.split()[0] if x else "")
            df_visual['Descripción'] = df_invest['Original (Würth)'].astype(str).apply(lambda x: x.split(maxsplit=1)[1].split('\n')[0] if len(x.split()) > 1 else "Sin Descripción")
            df_display = df_visual.drop_duplicates()

            seleccion = st.dataframe(
                df_display, use_container_width=True, hide_index=True,
                on_select="rerun", selection_mode="multi-row"
            )
            
            indices = seleccion.selection.rows
            if indices:
                codigos_sel = df_display.iloc[indices]['Código'].tolist()
                st.session_state['df_mkt_actual'] = df_invest[df_invest['Original (Würth)'].astype(str).str.startswith(tuple(codigos_sel))]
                st.session_state['nombres_seleccionados'] = df_display.iloc[indices]['Descripción'].tolist()

    df_mkt = st.session_state.get('df_mkt_actual', pd.DataFrame())
    
    # Inicialización de variables de control
    estrategia_sug = "Análisis en curso..."
    p_final_con_iva = 0.0
    es_contra_premium = False
    
    st.divider()

    # 2. Entradas del Usuario (Reactividad Instantánea)
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

    # Cálculo base
    precio_propuesto_neto = c_cif / (1 - (margen_objetivo / 100)) if margen_objetivo < 100 else c_cif

    # 3. Motor de Posicionamiento Dinámico
    if not df_mkt.empty:
        precios_ref = pd.to_numeric(df_mkt['P. Minorista'], errors='coerce').dropna().tolist()
        if precios_ref:
            promedio_mkt = sum(precios_ref) / len(precios_ref)
            
            # Detección de nivel de competencia (Calidad asignada por la IA)
            es_contra_premium = any(df_mkt['Calidad'].astype(str).str.contains('Premium|Líder|Alto', case=False, na=False))
            dif_vs_mkt = ((precio_propuesto_neto / promedio_mkt) - 1) * 100

            if es_contra_premium:
                estrategia_sug = "Paridad Competitiva"
                # Si el usuario quiere paridad, el sistema sugiere el promedio
                # Pero le permite al usuario "moverse" con el slider para ver el impacto
            elif dif_vs_mkt > 15: estrategia_sug = "Descreme (Premium)"
            elif dif_vs_mkt < -15: estrategia_sug = "Penetración de Mercado"
            else: estrategia_sug = "Paridad de Mercado"

    p_final_con_iva = precio_propuesto_neto * 1.22 if iva else precio_propuesto_neto

    # 4. MAPA DE POSICIONAMIENTO ESTILO "DASHBOARD"
    if not df_mkt.empty and not df_mkt['P. Minorista'].isnull().all():
        st.subheader(f"📊 Mapa de Posicionamiento: {estrategia_sug}")
        
        # Preparación de datos para la nube
        df_scatter = df_mkt[['Competidor', 'P. Minorista']].copy()
        df_scatter.columns = ['Vendedor', 'Precio']
        df_scatter['Precio'] = pd.to_numeric(df_scatter['Precio'], errors='coerce')
        df_scatter['Origen'] = 'Competencia'
        
        # Añadir Würth como la entidad dominante
        prop_row = pd.DataFrame({'Vendedor': ['WÜRTH (Propuesta)'], 'Precio': [precio_propuesto_neto], 'Origen': ['Würth']})
        df_scatter = pd.concat([df_scatter, prop_row], ignore_index=True)

        # Creación del gráfico con Plotly Express
        fig = px.scatter(
            df_scatter, 
            x="Precio", 
            y="Vendedor", 
            color="Origen",
            size=df_scatter['Origen'].map({'Competencia': 12, 'Würth': 35}), # Burbuja de Würth mucho más grande
            color_discrete_map={'Competencia': '#3498db', 'Würth': '#e74c3c'}, # Azul vs Rojo intenso
            hover_name="Vendedor",
            template="plotly_white"
        )

        # Líneas de referencia (Suelo, Techo, Medio)
        fig.add_vline(x=min(precios_ref), line_dash="dash", line_color="#95a5a6", 
                     annotation_text="Suelo Competencia", annotation_position="top left")
        fig.add_vline(x=max(precios_ref), line_dash="dash", line_color="#95a5a6", 
                     annotation_text="Techo Competencia", annotation_position="top right")
        fig.add_vline(x=promedio_mkt, line_width=2, line_color="#2ecc71", 
                     annotation_text="Precio Medio Mercado", annotation_position="bottom right")

        # Ajustes estéticos finales
        fig.update_layout(
            xaxis_title="Precio Unitario (USD)",
            yaxis_title="Vendedores / Competidores",
            showlegend=False,
            height=500,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        st.plotly_chart(fig, use_container_width=True)

        # Bloque de análisis del "Cerebro"
        with st.container():
            st.info(f"💡 **Veredicto Estratégico:** {estrategia_sug}")
            if es_contra_premium:
                st.write("Se ha detectado competencia de **Alto Desempeño**. Su precio propuesto se mantiene en el rango de marcas líderes, asegurando el posicionamiento Premium de Würth.")
            else:
                st.write("Frente a competidores de segmento estándar, Würth mantiene una ventaja competitiva basada en calidad percibida.")

    # 5. RESULTADOS FINALES (KPIs)
    st.divider()
    res1, res2, res3 = st.columns(3)
    res1.metric("Costo CIF Final", f"{c_cif:,.2f}")
    res2.metric("PVP Final Sugerido", f"{p_final_con_iva:,.2f}")
    m_real = ((precio_propuesto_neto - c_cif) / precio_propuesto_neto * 100) if precio_propuesto_neto > 0 else 0
    res3.metric("Margen Real Bruto", f"{m_real:.1f}%")

    if st.button("📥 Exportar Análisis Estratégico"):
        output = BytesIO()
        df_res = pd.DataFrame({
            "Métrica": ["Productos Analizados", "Costo CIF", "Precio Propuesto (Neto)", "PVP Final (IVA)", "Margen Final %", "Estrategia Aplicada"],
            "Valor": [", ".join(st.session_state.get('nombres_seleccionados', [])), f"{c_cif:.2f}", f"{precio_propuesto_neto:.2f}", f"{p_final_con_iva:.2f}", f"{m_real:.1f}%", estrategia_sug]
        })
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_res.to_excel(writer, index=False)
        st.download_button("💾 Descargar Reporte en Excel", output.getvalue(), "Estrategia_Precios_Wuerth.xlsx")
