import streamlit as st
import pandas as pd
from io import BytesIO

def mostrar_fijacion_precios():
    st.header("💰 Módulo de Fijación de Precios")
    
    precios_referencia = []
    nombres_para_reporte = []
    
    # 1. Sincronizar productos (Interfaz de Tabla Espejo del Excel)
    if 'resultados_investigacion' in st.session_state:
        with st.expander("📥 Sincronizar productos", expanded=True):
            df_invest = pd.DataFrame(st.session_state['resultados_investigacion'])
            
            # --- LIMPIEZA DE COLUMNAS ---
            # Creamos un DataFrame que solo tenga lo que tú necesitas ver
            # 'CODIGO' y 'DESCRIPCION CORTA' (o sus equivalentes en el DF procesado)
            df_visual = pd.DataFrame()
            
            # Intentamos detectar las columnas originales
            df_visual['Código'] = df_invest['Original (Würth)'].astype(str).str.split().str[0]
            # Tomamos el resto como descripción, ignorando saltos de línea de la IA
            df_visual['Descripción'] = df_invest['Original (Würth)'].astype(str).str.split(n=1).str[1].str.split('\n').str[0]
            
            st.write("Selecciona las filas de los productos que deseas analizar:")
            
            # Tabla interactiva con columnas independientes
            seleccion = st.dataframe(
                df_visual.drop_duplicates(),
                use_container_width=True,
                hide_index=True,
                on_select="rerun",
                selection_mode="multi-row"
            )
            
            filas_indices = seleccion.selection.rows
            
            if st.button("Confirmar Selección de Productos"):
                if filas_indices:
                    # Recuperamos los códigos de las filas marcadas
                    codigos_elegidos = df_visual.iloc[filas_indices]['Código'].tolist()
                    
                    # Filtramos el origen para obtener los precios de esos códigos
                    df_filtrado = df_invest[df_invest['Original (Würth)'].str.contains('|'.join(codigos_elegidos))]
                    
                    col_precio = next((c for c in ['P. Minorista', 'Precio', 'precio_minorista'] if c in df_filtrado.columns), None)
                    
                    if col_precio:
                        precios_ref = pd.to_numeric(df_filtrado[col_precio], errors='coerce').dropna().tolist()
                        st.session_state['precios_sincronizados'] = precios_ref
                        st.session_state['seleccion_nombres'] = df_visual.iloc[filas_indices]['Descripción'].tolist()
                        st.success(f"✅ Sincronizados {len(precios_ref)} precios de la competencia.")
                    else:
                        st.error("No se encontraron precios numéricos para esta selección.")
                else:
                    st.warning("Debe seleccionar al menos una fila de la tabla.")

    # Recuperar datos de la sesión para los cálculos
    if 'precios_sincronizados' in st.session_state:
        precios_referencia = st.session_state['precios_sincronizados']
        nombres_para_reporte = st.session_state.get('seleccion_nombres', [])

    st.divider()

    # 2. Resumen de Competencia (Lo que ayuda a decidir)
    promedio_mkt = 0
    if precios_referencia:
        st.subheader("📊 Referencia de Mercado")
        m1, m2, m3 = st.columns(3)
        promedio_mkt = sum(precios_referencia) / len(precios_referencia)
        m1.metric("Promedio", f"{promedio_mkt:,.2f}")
        m2.metric("Mínimo", f"{min(precios_referencia):,.2f}")
        m3.metric("Máximo", f"{max(precios_referencia):,.2f}")
        st.divider()

    # 3. Costos y Estrategia
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

    # 4. Cálculo Final
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

    if st.button("📥 EXPORTAR ANÁLISIS A EXCEL"):
        df_resumen = pd.DataFrame({
            "Producto(s)": [", ".join(nombres_para_reporte)],
            "Costo CIF": [costo_cif],
            "Precio Sugerido": [precio_final],
            "Margen %": [f"{margen_real:.1f}%"],
            "Promedio Competencia": [promedio_mkt]
        })
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_resumen.to_excel(writer, index=False)
        st.download_button("💾 Descargar", output.getvalue(), "Analisis_Wuerth.xlsx")
