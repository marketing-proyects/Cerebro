import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

def mostrar_fijacion_precios():
    st.header("💰 Módulo de Fijación de Precios")
    
    # 1. SELECCIÓN DE PRODUCTOS (Lógica de extracción blindada)
    if 'resultados_investigacion' in st.session_state:
        with st.expander("📥 Selección de Productos", expanded=True):
            df_invest = pd.DataFrame(st.session_state['resultados_investigacion'])
            
            # Limpieza robusta para recuperar descripciones
            df_visual = pd.DataFrame()
            df_visual['Código'] = df_invest['Original (Würth)'].astype(str).apply(lambda x: x.split()[0] if len(x.split()) > 0 else "S/C")
            # Recuperamos la descripción completa después del primer espacio
            df_visual['Descripción'] = df_invest['Original (Würth)'].astype(str).apply(lambda x: " ".join(x.split()[1:]) if len(x.split()) > 1 else "Sin descripción")
            df_display = df_visual.drop_duplicates()

            seleccion = st.dataframe(
                df_display, use_container_width=True, hide_index=True,
                on_select="rerun", selection_mode="multi-row"
            )
            
            indices = seleccion.selection.rows
            if indices:
                codigos_sel = df_display.iloc[indices]['Código'].tolist()
                # Filtramos garantizando que coincidan los códigos
                st.session_state['df_mkt_actual'] = df_invest[df_invest['Original (Würth)'].astype(str).str.contains('|'.join(codigos_sel))]
                st.session_state['nombres_seleccionados'] = df_display.iloc[indices]['Descripción'].tolist()

    df_mkt = st.session_state.get('df_mkt_actual', pd.DataFrame())
    
    # Inicialización de variables de seguridad
    estrategia_sug = "Pendiente de datos"
    p_final_con_iva = 0.0
    es_contra_premium = False
    
    st.divider()

    # 2. VARIABLES COMERCIALES
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

    precio_base_neto = c_cif / (1 - (margen_objetivo / 100)) if margen_objetivo < 100 else c_cif

    # 3. MOTOR DE DECISIÓN (Basado en Calidad de la IA)
    if not df_mkt.empty:
        precios_ref = pd.to_numeric(df_mkt['P. Minorista'], errors='coerce').dropna().tolist()
        if precios_ref:
            promedio_mkt = sum(precios_ref) / len(precios_ref)
            es_contra_premium = any(df_mkt['Calidad'].astype(str).str.contains('Premium|Líder|Alto', case=False, na=False))
            dif_vs_mkt = ((precio_base_neto / promedio_mkt) - 1) * 100

            if es_contra_premium:
                estrategia_sug = "Paridad Competitiva"
                # Forzamos la sugerencia al promedio si hay marcas pro
                precio_base_neto = promedio_mkt
            elif dif_vs_mkt > 15: estrategia_sug = "Descreme"
            elif dif_vs_mkt < -15: estrategia_sug = "Penetración"
            else: estrategia_sug = "Paridad de Mercado"

    p_final_con_iva = precio_base_neto * 1.22 if iva else precio_base_neto

    # 4. MAPA DE POSICIONAMIENTO PREMIUM (Estilo Dispersión Dinámica)
    if not df_mkt.empty and not df_mkt['P. Minorista'].isnull().all():
        st.subheader(f"📊 Mapa de Posicionamiento: {estrategia_sug}")
        
        # Preparación de Nube de Datos
        df_scatter = df_mkt[['Competidor', 'P. Minorista']].copy()
        df_scatter.columns = ['Vendedor', 'Precio']
        df_scatter['Precio'] = pd.to_numeric(df_scatter['Precio'], errors='coerce')
        df_scatter['Tipo'] = 'Competencia'
        
        # Inserción destacada de Würth
        prop_row = pd.DataFrame({'Vendedor': ['PROPUESTA WÜRTH'], 'Precio': [precio_base_neto], 'Tipo': ['Würth']})
        df_scatter = pd.concat([df_scatter, prop_row], ignore_index=True)

        fig = px.scatter(
            df_scatter, x="Precio", y="Vendedor", color="Tipo",
            color_discrete_map={'Competencia': '#3498db', 'Würth': '#e74c3c'},
            size=df_scatter['Tipo'].map({'Competencia': 12, 'Würth': 35}), # Burbuja roja dominante
            template="plotly_white"
        )
        
        # Líneas de referencia estratégicas
        fig.add_vline(x=min(precios_ref), line_dash="dash", line_color="#95a5a6", annotation_text="Suelo")
        fig.add_vline(x=max(precios_ref), line_dash="dash", line_color="#95a5a6", annotation_text="Techo")
        fig.add_vline(x=promedio_mkt, line_width=2, line_color="#2ecc71", annotation_text="Media Mercado")
        
        fig.update_layout(showlegend=False, height=500, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)

        # Análisis narrativo del Cerebro
        st.info(f"💡 **Análisis:** " + 
                (f"Al competir contra marcas Premium, se sugiere **Paridad**. " if es_contra_premium else f"Se sugiere **{estrategia_sug}**. ") + 
                "Tu posición está marcada por la burbuja roja frente al ecosistema de precios detectado.")

    # 5. RESULTADOS Y EXPORTACIÓN
    st.divider()
    r1, r2, r3 = st.columns(3)
    r1.metric("Costo CIF", f"{c_cif:,.2f}")
    r2.metric("PVP Final", f"{p_final_con_iva:,.2f}")
    m_real = ((precio_base_neto - c_cif) / precio_base_neto * 100) if precio_base_neto > 0 else 0
    r3.metric("Margen Real", f"{m_real:.1f}%")

    if st.button("📥 Exportar Análisis"):
        output = BytesIO()
        df_res = pd.DataFrame({
            "Parámetro": ["Productos Seleccionados", "Costo CIF", "Precio Sugerido", "Estrategia"],
            "Valor": [", ".join(st.session_state.get('nombres_seleccionados', [])), c_cif, p_final_con_iva, estrategia_sug]
        })
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_res.to_excel(writer, index=False)
        st.download_button("💾 Bajar Excel", output.getvalue(), "Pricing_Wuerth_Scatter.xlsx")
