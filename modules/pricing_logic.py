import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

def mostrar_fijacion_precios():
    st.header("💰 Módulo de Fijación de Precios")
    
    # 1. VISOR DE RESULTADOS Y SELECCIÓN (Blindaje Total)
    # Verificamos si hay datos y si el DataFrame no está vacío
    if 'resultados_investigacion' in st.session_state and len(st.session_state['resultados_investigacion']) > 0:
        df_invest = pd.DataFrame(st.session_state['resultados_investigacion'])
        
        # Identificamos las columnas dinámicamente para evitar el KeyError
        col_principal = next((c for c in df_invest.columns if "Original" in c or "Würth" in c), None)
        col_adn = next((c for c in df_invest.columns if "ADN" in c or "Identificado" in c), None)

        # Forzamos que el preview sea siempre visible
        with st.container():
            st.subheader("📊 Vista Previa de la Investigación")
            st.dataframe(df_invest, use_container_width=True, hide_index=True)
            
            if col_principal:
                st.subheader("📥 Selección de Productos para el Mapa de Precios")
                
                # Creamos la tabla de selección con el ADN recuperado
                df_sel = pd.DataFrame()
                df_sel['Código'] = df_invest[col_principal].astype(str).str.split().str[0]
                
                if col_adn:
                    df_sel['Descripción'] = df_invest[col_adn].fillna("Descripción General")
                else:
                    df_sel['Descripción'] = df_invest[col_principal].astype(str).str.split(n=1).str[1]
                
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
                    # Sincronizamos con los datos de mercado
                    mask = df_invest[col_principal].astype(str).str.startswith(tuple(codigos_seleccionados))
                    st.session_state['df_mkt_actual'] = df_invest[mask]
                    st.session_state['nombres_seleccionados'] = df_sel.iloc[indices]['Descripción'].tolist()
            else:
                st.error("❌ Error de formato: No se encontró la columna de inventario.")
    else:
        st.info("ℹ️ Realiza una investigación de mercado exitosa para visualizar el preview y analizar precios.")

    df_mkt = st.session_state.get('df_mkt_actual', pd.DataFrame())
    st.divider()

    # 2. VARIABLES COMERCIALES
    col_c, col_e = st.columns(2)
    with col_c:
        st.subheader("📦 Costos")
        c_fabrica = st.number_input("Costo de Fábrica", min_value=0.0, step=0.1, value=5.00)
        g_import = st.number_input("Gastos Importación (%)", min_value=0.0, step=0.1, value=40.0)
        c_cif = c_fabrica * (1 + (g_import / 100))
        st.metric("Costo CIF (Unitario)", f"{c_cif:,.2f}")

    with col_e:
        st.subheader("📈 Margen")
        margen = st.slider("Margen de Utilidad Deseado (%)", 0, 100, 35)
        iva = st.checkbox("Incluir IVA Uruguay (22%)", value=True)

    # 3. LÓGICA DE POSICIONAMIENTO
    precio_base = c_cif / (1 - (margen / 100)) if margen < 100 else c_cif
    estrategia_actual = "Análisis de Costos"

    if not df_mkt.empty:
        precios_ref = pd.to_numeric(df_mkt['P. Minorista'], errors='coerce').dropna().tolist()
        if precios_ref:
            promedio_mercado = sum(precios_ref) / len(precios_ref)
            # Detección de calidad Premium para sugerencia automática
            es_premium = any(df_mkt['Calidad'].astype(str).str.contains('Premium|Líder|Alto', case=False, na=False)) if 'Calidad' in df_mkt.columns else False
            
            if es_premium:
                precio_base = promedio_mercado
                estrategia_actual = "Paridad Competitiva"
            else:
                estrategia_actual = "Paridad de Mercado"

    p_final_total = precio_base * 1.22 if iva else precio_base

    # 4. GRÁFICO DE PELOTITAS (X: Actor, Y: Precio)
    if not df_mkt.empty and not df_mkt['P. Minorista'].isnull().all():
        st.subheader(f"🏁 Estrategia Sugerida: {estrategia_actual}")
        
        df_plot = df_mkt[['Competidor', 'P. Minorista']].copy()
        df_plot.columns = ['Actor', 'Precio']
        df_plot['Precio'] = pd.to_numeric(df_plot['Precio'], errors='coerce')
        df_plot['Tipo'] = 'Competencia'
        
        # Inserción de la Pelotita Roja de Würth
        prop_row = pd.DataFrame({'Actor': ['WÜRTH'], 'Precio': [precio_base], 'Tipo': ['Würth']})
        df_plot = pd.concat([df_plot, prop_row], ignore_index=True)

        fig = px.scatter(
            df_plot, x="Actor", y="Precio", color="Tipo",
            color_discrete_map={'Competencia': '#1f77b4', 'Würth': '#FF0000'},
            size=[15] * (len(df_plot)-1) + [35], # Pelotita roja más grande
            title="Comparativa de Precios: Würth vs Competencia"
        )
        fig.update_layout(showlegend=False, height=450)
        st.plotly_chart(fig, use_container_width=True)

    # 5. RESULTADOS KPI
    st.divider()
    r1, r2, r3 = st.columns(3)
    r1.metric("CIF Final", f"{c_cif:,.2f}")
    r2.metric("PVP Final Sugerido", f"{p_final_total:,.2f}")
    m_real = ((precio_base - c_cif) / precio_base * 100) if precio_base > 0 else 0
    r3.metric("Margen Real Bruto", f"{m_real:.1f}%")
