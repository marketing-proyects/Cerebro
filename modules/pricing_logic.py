import streamlit as st
import pandas as pd
from io import BytesIO

def mostrar_fijacion_precios():
    st.header("💰 Módulo de Fijación de Precios")
    
    # 1. SINCRONIZACIÓN AUTOMÁTICA
    if 'resultados_investigacion' in st.session_state:
        with st.expander("📥 Selección de Productos", expanded=True):
            df_invest = pd.DataFrame(st.session_state['resultados_investigacion'])
            
            # Limpieza para asegurar que vemos Código y Descripción Corta
            # Usamos las columnas originales del Excel cargado
            df_visual = df_invest[['Original (Würth)', 'ADN Identificado']].drop_duplicates()
            df_visual.columns = ['Producto (Código/Nombre)', 'Referencia Mercado']

            seleccion = st.dataframe(
                df_visual,
                use_container_width=True,
                hide_index=True,
                on_select="rerun",
                selection_mode="multi-row"
            )
            
            # Guardamos la selección en el estado para reactividad
            indices = seleccion.selection.rows
            if indices:
                codigos = df_visual.iloc[indices]['Producto (Código/Nombre)'].tolist()
                df_filtrado = df_invest[df_invest['Original (Würth)'].isin(codigos)]
                st.session_state['precios_mkt'] = pd.to_numeric(df_filtrado['P. Minorista'], errors='coerce').dropna().tolist()
                st.session_state['nombres_seleccionados'] = codigos
            else:
                st.session_state['precios_mkt'] = []

    # Recuperar datos de mercado
    precios_ref = st.session_state.get('precios_mkt', [])
    promedio_mkt = sum(precios_ref) / len(precios_ref) if precios_ref else 0

    st.divider()

    # 2. ENTRADA DE DATOS (REACTIVE INPUTS)
    col_c, col_e = st.columns(2)
    with col_c:
        st.subheader("📦 Costo de Importación")
        c_fabrica = st.number_input("Costo de Fábrica (Origen)", min_value=0.0, step=0.01, value=5.00)
        g_import = st.number_input("Gastos de Importación/Aduana (%)", min_value=0.0, value=40.0)
        c_cif = c_fabrica * (1 + (g_import / 100))
        st.metric("Costo Unitario (CIF)", f"{c_cif:,.2f}")

    with col_e:
        st.subheader("📈 Margen y Estrategia")
        margen = st.slider("Margen de Utilidad Deseado (%)", 0, 100, 35)
        estrategia = st.selectbox("Estrategia Kotler", ["Basado en costo", "Paridad de mercado", "Descreme", "Penetración"])
        iva = st.checkbox("Incluir IVA Uruguay (22%)", value=True)

    # 3. CÁLCULO DINÁMICO (Sin botones)
    precio_neto = 0.0
    if estrategia == "Basado en costo" or not precios_ref:
        precio_neto = c_cif / (1 - (margen / 100)) if margen < 100 else c_cif
    elif estrategia == "Paridad de mercado":
        precio_neto = promedio_mkt
    elif estrategia == "Descreme":
        precio_neto = max(precios_ref) * 1.10
    elif estrategia == "Penetración":
        precio_neto = min(precios_ref) * 0.90

    precio_final = precio_neto * 1.22 if iva else precio_neto
    utilidad = precio_neto - c_cif
    margen_real = (utilidad / precio_neto * 100) if precio_neto > 0 else 0

    # 4. INSTANCIA DE POSICIONAMIENTO (Visualización)
    if precios_ref:
        st.subheader("🏁 Posicionamiento de Mercado")
        
        # Gráfico de barras simple para evitar errores de librería pesada
        chart_data = pd.DataFrame({
            "Puntos de Referencia": ["Mínimo Mkt", "Tu Propuesta", "Promedio Mkt", "Máximo Mkt"],
            "Precio": [min(precios_ref), precio_neto, promedio_mkt, max(precios_ref)]
        })
        st.bar_chart(chart_data, x="Puntos de Referencia", y="Precio", color="#ff4b4b")

        # Sugerencia Automática
        dif = ((precio_neto / promedio_mkt) - 1) * 100
        if dif > 15:
            st.error(f"⚠️ Estás un {dif:.1f}% por encima del mercado. Considera una estrategia de Descreme.")
        elif dif < -15:
            st.warning(f"💡 Estás un {abs(dif):.1f}% por debajo. Tienes espacio para subir el margen.")
        else:
            st.success(f"✅ Precio alineado con el mercado uruguayo (Dif: {dif:.1f}%).")

    # 5. RESULTADOS Y EXPORTACIÓN
    st.divider()
    r1, r2, r3 = st.columns(3)
    r1.metric("Costo CIF Final", f"{c_cif:,.2f}")
    r2.metric("PVP Sugerido", f"{precio_final:,.2f}")
    r3.metric("Margen Real", f"{margen_real:.1f}%")

    if st.button("📥 EXPORTAR ANÁLISIS FINAL"):
        output = BytesIO()
        df_res = pd.DataFrame({
            "Parámetro": ["Productos", "CIF", "PVP Final", "Margen %", "Estrategia"],
            "Valor": [", ".join(st.session_state.get('nombres_seleccionados', [])), c_cif, precio_final, f"{margen_real:.1f}%", estrategia]
        })
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_res.to_excel(writer, index=False)
        st.download_button("💾 Bajar Excel", output.getvalue(), "Pricing_Wuerth.xlsx")
