import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

def mostrar_fijacion_precios():
    st.header("💰 Módulo de Fijación de Precios")
    
    # 1. RESTAURACIÓN DEL PREVIEW Y SELECCIÓN (Sin KeyErrors)
    if 'resultados_investigacion' in st.session_state:
        df_invest = pd.DataFrame(st.session_state['resultados_investigacion'])
        
        # Identificación flexible de columnas para evitar KeyErrors
        col_id = next((c for c in df_invest.columns if "Original" in c or "Würth" in c), df_invest.columns[0])
        col_adn = next((c for c in df_invest.columns if "ADN" in c or "Identificado" in c), None)

        with st.expander("📊 Vista Previa de la Investigación", expanded=True):
            # Mostramos el preview directo tal como funcionaba antes
            st.dataframe(df_invest.head(10), use_container_width=True, hide_index=True)
            
            st.subheader("📥 Selección de Productos para Análisis")
            # Creamos una tabla simplificada para seleccionar
            df_sel = pd.DataFrame()
            df_sel['Código'] = df_invest[col_id].astype(str).str.split().str[0]
            
            # Recuperamos el ADN (palabras clave) para la descripción clara
            if col_adn:
                df_sel['Descripción'] = df_invest[col_adn].fillna("Descripción no generada")
            else:
                # Si el ADN falló, usamos las primeras palabras del original
                df_sel['Descripción'] = df_invest[col_id].astype(str).str.split(n=1).str[1].str.split('\n').str[0]
            
            df_sel = df_sel.drop_duplicates()

            seleccion = st.dataframe(
                df_sel, 
                use_container_width=True, 
                hide_index=True,
                on_select="rerun", 
                selection_mode="multi-row"
            )
            
            indices = seleccion.selection.rows
            if indices:
                codigos_seleccionados = df_sel.iloc[indices]['Código'].tolist()
                mask = df_invest[col_id].astype(str).str.startswith(tuple(codigos_seleccionados))
                st.session_state['df_mkt_actual'] = df_invest[mask]
                st.session_state['nombres_seleccionados'] = df_sel.iloc[indices]['Descripción'].tolist()

    df_mkt = st.session_state.get('df_mkt_actual', pd.DataFrame())
    st.divider()

    # 2. VARIABLES DE COSTO (Reactividad Instantánea)
    col_c, col_e = st.columns(2)
    with col_c:
        st.subheader("📦 Costo de Importación")
        c_fabrica = st.number_input("Costo de Fábrica (Origen)", min_value=0.0, step=0.1, value=5.00)
        g_import = st.number_input("Gastos Importación (%)", min_value=0.0, step=0.1, value=40.0)
        c_cif = c_fabrica * (1 + (g_import / 100))
        st.metric("Costo Unitario (CIF)", f"{c_cif:,.2f}")

    with col_e:
        st.subheader("📈 Margen Deseado")
        margen_objetivo = st.slider("Margen de Utilidad (%)", 0, 100, 35)
        iva = st.checkbox("Incluir IVA (22%)", value=True)

    # 3. MOTOR DE POSICIONAMIENTO
    p_base_neto = c_cif / (1 - (margen_objetivo / 100)) if margen_objetivo < 100 else c_cif
    estrategia_actual = "Basado en Costo"

    if not df_mkt.empty:
        p_ref = pd.to_numeric(df_mkt['P. Minorista'], errors='coerce').dropna().tolist()
        if p_ref:
            promedio = sum(p_ref) / len(p_ref)
            # Detección de nivel según calidad detectada por IA
            es_pro = any(df_mkt['Calidad'].astype(str).str.contains('Premium|Líder|Alto', case=False, na=False)) if 'Calidad' in df_mkt.columns else False
            
            if es_pro:
                estrategia_actual = "Paridad Competitiva"
                p_base_neto = promedio # Sugerencia inteligente
            else:
                estrategia_actual = "Paridad de Mercado"

    p_final = p_base_neto * 1.22 if iva else p_base_neto

    # 4. GRÁFICO DE PELOTITAS (Horizontal: Actores, Vertical: Precio)
    if not df_mkt.empty and not df_mkt['P. Minorista'].isnull().all():
        st.subheader(f"🏁 Veredicto: {estrategia_actual}")
        
        df_p = df_mkt[['Competidor', 'P. Minorista']].copy()
        df_p.columns = ['Actor', 'Precio']
        df_p['Precio'] = pd.to_numeric(df_p['Precio'], errors='coerce')
        df_p['Tipo'] = 'Competencia'
        
        # Pelotita Roja WÜRTH
        prop = pd.DataFrame({'Actor': ['WÜRTH'], 'Precio': [p_base_neto], 'Tipo': ['Würth']})
        df_p = pd.concat([df_p, prop], ignore_index=True)

        fig = px.scatter(
            df_p, x="Actor", y="Precio", color="Tipo",
            color_discrete_map={'Competencia': '#1f77b4', 'Würth': '#FF0000'},
            size=[15] * (len(df_p)-1) + [32],
            title="Comparativa: Würth vs Actores del Mercado"
        )
        fig.update_layout(showlegend=False, height=450)
        st.plotly_chart(fig, use_container_width=True)

    # 5. RESULTADOS
    st.divider()
    r1, r2, r3 = st.columns(3)
    r1.metric("Costo CIF", f"{c_cif:,.2f}")
    r2.metric("PVP Final", f"{p_final:,.2f}")
    m_real = ((p_base_neto - c_cif) / p_base_neto * 100) if p_base_neto > 0 else 0
    r3.metric("Margen Real", f"{m_real:.1f}%")
