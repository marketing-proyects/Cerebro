import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

def mostrar_fijacion_precios():
    st.header("💰 Módulo de Fijación de Precios")
    
    # 1. RECUPERACIÓN DE DATOS Y PREVIEW (Versión Estable)
    if 'resultados_investigacion' in st.session_state:
        df_invest = pd.DataFrame(st.session_state['resultados_investigacion'])
        
        with st.expander("📊 Resultados de la Investigación (Preview)", expanded=True):
            # Restauramos el preview directo que permitía ver los datos sin descargar
            st.dataframe(df_invest, use_container_width=True, hide_index=True)
            
            st.subheader("📥 Selección de Productos")
            # Lógica recuperada: Código + ADN Identificado (Palabras clave IA)
            df_sel = pd.DataFrame()
            df_sel['Código'] = df_invest['Original (Würth)'].astype(str).str.split().str[0]
            
            # Verificación de seguridad para la columna ADN
            if 'ADN Identificado' in df_invest.columns:
                df_sel['Descripción'] = df_invest['ADN Identificado'].fillna("Sin ADN")
            else:
                df_sel['Descripción'] = df_invest['Original (Würth)'].astype(str).str.split(n=1).str[1]

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
                codigos = df_sel.iloc[indices]['Código'].tolist()
                mask = df_invest['Original (Würth)'].astype(str).str.startswith(tuple(codigos))
                st.session_state['df_mkt_actual'] = df_invest[mask]
                st.session_state['nombres_seleccionados'] = df_sel.iloc[indices]['Descripción'].tolist()

    df_mkt = st.session_state.get('df_mkt_actual', pd.DataFrame())
    st.divider()

    # 2. VARIABLES COMERCIALES
    col_c, col_e = st.columns(2)
    with col_c:
        st.subheader("📦 Costo de Importación")
        c_fabrica = st.number_input("Costo de Fábrica", min_value=0.0, step=0.1, value=5.00)
        g_import = st.number_input("Gastos Importación (%)", min_value=0.0, step=0.1, value=40.0)
        c_cif = c_fabrica * (1 + (g_import / 100))
        st.metric("Costo CIF", f"{c_cif:,.2f}")

    with col_e:
        st.subheader("📈 Margen")
        margen = st.slider("Margen Deseado (%)", 0, 100, 35)
        iva = st.checkbox("Incluir IVA (22%)", value=True)

    # 3. LÓGICA DE PRECIO AUTOMÁTICA (Sin Menú Kotler)
    precio_base = c_cif / (1 - (margen / 100)) if margen < 100 else c_cif
    
    if not df_mkt.empty:
        precios_ref = pd.to_numeric(df_mkt['P. Minorista'], errors='coerce').dropna().tolist()
        if precios_ref:
            promedio = sum(precios_ref) / len(precios_ref)
            # Detección de calidad Premium según análisis previo de la IA
            es_premium = any(df_mkt['Calidad'].astype(str).str.contains('Premium|Líder|Alto', case=False, na=False))
            
            if es_premium:
                precio_base = promedio # Sugerencia de Paridad contra marcas Pro
                estrategia = "Paridad Competitiva"
            else:
                estrategia = "Basado en Costo"

    precio_final = precio_base * 1.22 if iva else precio_base

    # 4. GRÁFICO DE COMPARATIVA SIMPLE (Pelotitas)
    if not df_mkt.empty and not df_mkt['P. Minorista'].isnull().all():
        st.subheader("🏁 Posicionamiento Würth")
        
        df_p = df_mkt[['Competidor', 'P. Minorista']].copy()
        df_p.columns = ['Actor', 'Precio']
        df_p['Precio'] = pd.to_numeric(df_p['Precio'], errors='coerce')
        df_p['Marca'] = 'Competencia'
        
        # Agregamos la pelotita de Würth
        prop = pd.DataFrame({'Actor': ['WÜRTH'], 'Precio': [precio_base], 'Marca': ['Würth']})
        df_p = pd.concat([df_p, prop], ignore_index=True)

        # Gráfico de dispersión: Actores en X, Precio en Y
        fig = px.scatter(
            df_p, x="Actor", y="Precio", color="Marca",
            color_discrete_map={'Competencia': '#1f77b4', 'Würth': '#FF0000'},
            size=[15] * (len(df_p)-1) + [30],
            title="Comparativa de Precios"
        )
        st.plotly_chart(fig, use_container_width=True)

    # 5. RESULTADOS
    st.divider()
    r1, r2, r3 = st.columns(3)
    r1.metric("CIF Final", f"{c_cif:,.2f}")
    r2.metric("PVP Sugerido", f"{precio_final:,.2f}")
    m_real = ((precio_base - c_cif) / precio_base * 100) if precio_base > 0 else 0
    r3.metric("Margen Real", f"{m_real:.1f}%")
