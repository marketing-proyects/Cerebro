import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

def mostrar_fijacion_precios():
    st.header("💰 Módulo de Fijación de Precios")
    
    # Inicialización de estados
    if 'precios_sincronizados' not in st.session_state:
        st.session_state['precios_sincronizados'] = []
    if 'competidores_completos' not in st.session_state:
        st.session_state['competidores_completos'] = pd.DataFrame()

    # 1. Sincronizar productos (Mapeo directo de columnas)
    if 'resultados_investigacion' in st.session_state:
        with st.expander("📥 Sincronizar productos del Inventario", expanded=True):
            df_invest = pd.DataFrame(st.session_state['resultados_investigacion'])
            
            # Mostramos la tabla para selección, asegurando que se vean las columnas originales
            # Usamos 'Original (Würth)' como referencia para el Código
            st.write("Selecciona los productos para el análisis de posicionamiento:")
            
            seleccion = st.dataframe(
                df_invest[['Original (Würth)', 'ADN Identificado']].drop_duplicates(),
                use_container_width=True,
                hide_index=True,
                on_select="rerun",
                selection_mode="multi-row"
            )
            
            indices = seleccion.selection.rows
            
            if st.button("Confirmar y Analizar Mercado"):
                if indices:
                    codigos_eleccion = df_invest.iloc[indices]['Original (Würth)'].tolist()
                    df_filtrado = df_invest[df_invest['Original (Würth)'].isin(codigos_eleccion)]
                    
                    # Guardamos precios y el dataframe completo para el gráfico
                    st.session_state['precios_sincronizados'] = pd.to_numeric(df_filtrado['P. Minorista'], errors='coerce').dropna().tolist()
                    st.session_state['competidores_completos'] = df_filtrado
                    st.success(f"✅ Datos cargados para {len(codigos_eleccion)} productos.")
                else:
                    st.warning("Selecciona al menos una fila.")

    st.divider()

    # 2. Costos y Estrategia
    col_c, col_e = st.columns(2)
    with col_c:
        st.subheader("📦 Costos de Importación")
        c_fabrica = st.number_input("Costo de Fábrica (Origen)", min_value=0.0, step=0.01, value=5.00)
        g_import = st.number_input("Gastos Importación/Aduana (%)", min_value=0.0, value=40.0)
        c_cif = c_fabrica * (1 + (g_import / 100))
        st.metric("Costo CIF Final", f"{c_cif:,.2f}")

    with col_e:
        st.subheader("📈 Margen y Posicionamiento")
        margen = st.slider("Margen Deseado (%)", 0, 100, 35)
        estrategia = st.selectbox("Estrategia Kotler", ["Basado en costo", "Paridad de mercado", "Descreme", "Penetración"])
        iva = st.checkbox("IVA Uruguay (22%)", value=True)

    # Lógica de cálculo
    precios_ref = st.session_state['precios_sincronizados']
    precio_neto = 0.0
    if estrategia == "Basado en costo" or not precios_ref:
        precio_neto = c_cif / (1 - (margen / 100)) if margen < 100 else c_cif
    elif estrategia == "Paridad de mercado":
        precio_neto = sum(precios_ref) / len(precios_ref)
    elif estrategia == "Descreme":
        precio_neto = max(precios_ref) * 1.10
    elif estrategia == "Penetración":
        precio_neto = min(precios_ref) * 0.90

    precio_final = precio_neto * 1.22 if iva else precio_neto
    
    # 3. INSTANCIA DE SUGERENCIA Y GRÁFICO (Cierre del módulo)
    if not st.session_state['competidores_completos'].empty:
        st.subheader("📊 Análisis Comparativo de Posicionamiento")
        
        # Preparamos datos para el gráfico de dispersión
        df_plot = st.session_state['competidores_completos'].copy()
        df_plot['Precio'] = pd.to_numeric(df_plot['P. Minorista'], errors='coerce')
        
        # Añadimos nuestra propuesta al gráfico para comparar
        nueva_fila = {'Competidor': 'NUESTRA PROPUESTA (Würth)', 'Precio': precio_neto, 'Calidad': 'Premium'}
        df_plot = pd.concat([df_plot, pd.DataFrame([nueva_fila])], ignore_index=True)

        fig = px.scatter(df_plot, x="Precio", y="Calidad", color="Competidor", 
                         title="Gráfico de Dispersión: Precio vs Calidad",
                         labels={"Precio": "Precio Unitario (Neto)"},
                         size_max=15, symbol="Competidor")
        
        st.plotly_chart(fig, use_container_width=True)

        # Sugerencia de posicionamiento
        promedio = sum(precios_ref) / len(precios_ref)
        dif = ((precio_neto / promedio) - 1) * 100
        
        if dif > 10:
            st.error(f"⚠️ SUGERENCIA: Estás un {dif:.1f}% sobre el mercado. Recomendado para productos con alta exclusividad.")
        elif dif < -10:
            st.warning(f"💡 SUGERENCIA: Estás un {abs(dif):.1f}% bajo el promedio. Considera subir el margen para maximizar utilidad.")
        else:
            st.success(f"✅ SUGERENCIA: Posicionamiento óptimo. Estás alineado al promedio de mercado ({dif:.1f}% de diferencia).")

    # 4. Resultados y Exportación
    st.divider()
    res1, res2, res3 = st.columns(3)
    res1.metric("Costo CIF", f"{c_cif:,.2f}")
    res2.metric("PVP Final Sugerido", f"{precio_final:,.2f}")
    m_real = ((precio_neto - c_cif) / precio_neto * 100) if precio_neto > 0 else 0
    res3.metric("Margen Real Obtenido", f"{m_real:.1f}%")

    if st.button("📥 EXPORTAR ANÁLISIS FINAL"):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            pd.DataFrame({"Concepto": ["Estrategia", "CIF", "PVP Final", "Margen"], "Valor": [estrategia, c_cif, precio_final, f"{m_real:.1f}%"]}).to_excel(writer, index=False)
        st.download_button("💾 Descargar Excel", output.getvalue(), "Estrategia_Precios_Wuerth.xlsx")
