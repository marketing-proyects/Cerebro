import streamlit as st
import pandas as pd
from io import BytesIO

def mostrar_fijacion_precios():
    st.header("💰 Módulo de Fijación de Precios")
    
    precios_referencia = []
    nombres_para_reporte = []
    
    # 1. Sincronizar productos (Buscador Simplificado)
    if 'resultados_investigacion' in st.session_state:
        with st.expander("📥 Sincronizar productos", expanded=True):
            # Convertimos todo el DataFrame a String para evitar errores de tipo de dato
            df_invest = pd.DataFrame(st.session_state['resultados_investigacion']).astype(str)
            
            # Buscamos la columna que contiene la información original
            col_id = 'Original (Würth)' if 'Original (Würth)' in df_invest.columns else df_invest.columns[0]
            
            # --- NUEVA ESTRATEGIA: EXTRACCIÓN DIRECTA ---
            # Separamos el Código (primera palabra) y la Descripción (el resto de la primera línea)
            df_visual = pd.DataFrame()
            df_visual['Código'] = df_invest[col_id].apply(lambda x: x.split()[0] if len(x.split()) > 0 else "N/A")
            df_visual['Descripción'] = df_invest[col_id].apply(lambda x: x.split('\n')[0].split(' ', 1)[1] if len(x.split('\n')[0].split(' ', 1)) > 1 else "Sin nombre")

            st.write("Selecciona los productos para el escenario de precios:")
            
            # Tabla de selección independiente
            seleccion = st.dataframe(
                df_visual.drop_duplicates(),
                use_container_width=True,
                hide_index=True,
                on_select="rerun",
                selection_mode="multi-row"
            )
            
            indices = seleccion.selection.rows
            
            if st.button("Confirmar Selección"):
                if indices:
                    codigos_eleccion = df_visual.iloc[indices]['Código'].tolist()
                    
                    # Filtramos los datos reales para obtener los precios
                    df_filtrado = df_invest[df_invest[col_id].str.contains('|'.join(codigos_eleccion), na=False)]
                    
                    # Buscamos columna de precio de forma flexible
                    col_p = next((c for c in ['P. Minorista', 'Precio'] if c in df_filtrado.columns), None)
                    
                    if col_p:
                        precios_ref = pd.to_numeric(df_filtrado[col_p], errors='coerce').dropna().tolist()
                        st.session_state['precios_sincronizados'] = precios_ref
                        st.session_state['nombres_sincronizados'] = df_visual.iloc[indices]['Descripción'].tolist()
                        st.success(f"✅ Se sincronizaron {len(precios_ref)} precios.")
                    else:
                        st.error("No se encontraron precios en la investigación.")
                else:
                    st.warning("Selecciona al menos una fila.")

    # Recuperar datos para el motor financiero
    if 'precios_sincronizados' in st.session_state:
        precios_referencia = st.session_state['precios_sincronizados']
        nombres_para_reporte = st.session_state.get('nombres_sincronizados', [])

    st.divider()

    # 2. Resumen de Competencia
    promedio_mkt = 0
    if precios_referencia:
        st.subheader("📊 Indicadores de Mercado")
        m1, m2, m3 = st.columns(3)
        promedio_mkt = sum(precios_referencia) / len(precios_referencia)
        m1.metric("Promedio Mercado", f"{promedio_mkt:,.2f}")
        m2.metric("Mínimo", f"{min(precios_referencia):,.2f}")
        m3.metric("Máximo", f"{max(precios_referencia):,.2f}")
        st.divider()

    # 3. Costos (CIF Uruguay)
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("📦 Costo de Importación")
        costo_fabrica = st.number_input("Costo de Fábrica (Origen)", min_value=0.0, step=0.01, value=5.00)
        gastos_import = st.number_input("Gastos de Importación/Aduana (%)", min_value=0.0, step=0.1, value=40.0)
        costo_cif = costo_fabrica * (1 + (gastos_import / 100))
        st.metric("Costo CIF Final", f"{costo_cif:,.2f}")

    with c2:
        st.subheader("📈 Margen y Estrategia")
        margen = st.slider("Margen Deseado (%)", 0, 100, 35)
        estrategia = st.selectbox("Estrategia Kotler", ["Basado en costo", "Paridad de mercado", "Descreme", "Penetración"])
        iva = st.checkbox("IVA Uruguay (22%)", value=True)

    # 4. Cálculo
    precio_neto = 0.0
    if estrategia == "Basado en costo":
        precio_neto = costo_cif / (1 - (margen / 100)) if margen < 100 else costo_cif
    elif estrategia == "Paridad de mercado" and precios_referencia:
        precio_neto = promedio_mkt
    elif estrategia == "Descreme" and precios_referencia:
        precio_neto = max(precios_referencia) * 1.10
    elif estrategia == "Penetración" and precios_referencia:
        precio_neto = min(precios_referencia) * 0.90
    else:
        precio_neto = costo_cif / (1 - (margen / 100))

    precio_final = precio_neto * 1.22 if iva else precio_neto
    utilidad = precio_neto - costo_cif
    margen_real = (utilidad / precio_neto) * 100 if precio_neto > 0 else 0

    # 5. Resultados y Exportación
    st.subheader("🎯 Resultado")
    r1, r2, r3 = st.columns(3)
    r1.metric("Costo CIF", f"{costo_cif:,.2f}")
    r2.metric("PVP Final", f"{precio_final:,.2f}")
    r3.metric("Margen Real", f"{margen_real:.1f}%")

    if st.button("📥 EXPORTAR EXCEL"):
        df_res = pd.DataFrame({
            "Analisis": ["Productos", "Estrategia", "Costo CIF", "PVP Final", "Margen Real"],
            "Valores": [", ".join(nombres_para_reporte), estrategia, costo_cif, precio_final, f"{margen_real:.1f}%"]
        })
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_res.to_excel(writer, index=False)
        st.download_button("💾 Descargar", output.getvalue(), "Precios_Wuerth.xlsx")
