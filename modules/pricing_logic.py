import streamlit as st
import pandas as pd
from io import BytesIO

def mostrar_fijacion_precios():
    st.header("💰 Módulo de Fijación de Precios")
    
    precios_referencia = []
    nombres_para_reporte = []
    
    # 1. Sincronizar productos (Interfaz de Tabla de Selección Independiente)
    if 'resultados_investigacion' in st.session_state:
        with st.expander("📥 Sincronizar productos", expanded=True):
            # Cargamos los resultados previos
            df_invest = pd.DataFrame(st.session_state['resultados_investigacion'])
            
            # --- LIMPIEZA ROBUSTA DE DATOS ---
            # Identificamos la columna origen del Excel
            col_id = 'Original (Würth)' if 'Original (Würth)' in df_invest.columns else df_invest.columns[0]
            
            # Procesamos las columnas de forma segura para evitar el AttributeError
            def extraer_codigo(x):
                return str(x).split()[0] if pd.notnull(x) else "N/A"
            
            def extraer_descripcion(x):
                if pd.isnull(x): return "Sin Descripción"
                partes = str(x).split(maxsplit=1)
                # Tomamos solo la primera línea para evitar el análisis de la IA
                return partes[1].split('\n')[0] if len(partes) > 1 else "Sin Descripción"

            df_visual = pd.DataFrame()
            df_visual['Código'] = df_invest[col_id].apply(extraer_codigo)
            df_visual['Descripción'] = df_invest[col_id].apply(extraer_descripcion)
            
            st.write("Selecciona los productos de tu Excel para el análisis de precios:")
            
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
                    # Obtenemos los códigos marcados
                    codigos_elegidos = df_visual.iloc[filas_indices]['Código'].tolist()
                    
                    # Filtramos el origen usando los códigos seleccionados
                    # Usamos una búsqueda exacta para evitar falsos positivos
                    df_filtrado = df_invest[df_invest[col_id].astype(str).str.startswith(tuple(codigos_elegidos))]
                    
                    # Buscamos la columna de precios minoristas
                    col_precio = next((c for c in ['P. Minorista', 'Precio', 'precio_minorista'] if c in df_filtrado.columns), None)
                    
                    if col_precio:
                        precios_ref = pd.to_numeric(df_filtrado[col_precio], errors='coerce').dropna().tolist()
                        st.session_state['precios_sincronizados'] = precios_ref
                        st.session_state['seleccion_nombres'] = df_visual.iloc[filas_indices]['Descripción'].tolist()
                        st.success(f"✅ Sincronizados {len(precios_ref)} precios de competencia.")
                    else:
                        st.error("No se detectaron precios válidos en la investigación para esta selección.")
                else:
                    st.warning("Debes marcar al menos una fila en la tabla de arriba.")

    # Recuperar datos para los cálculos financieros
    if 'precios_sincronizados' in st.session_state:
        precios_referencia = st.session_state['precios_sincronizados']
        nombres_para_reporte = st.session_state.get('seleccion_nombres', [])

    st.divider()

    # 2. Resumen de Competencia (Métricas Clave)
    promedio_mkt = 0
    if precios_referencia:
        st.subheader("📊 Resumen de Competencia en Uruguay")
        m1, m2, m3 = st.columns(3)
        promedio_mkt = sum(precios_referencia) / len(precios_referencia)
        m1.metric("Promedio Mercado", f"{promedio_mkt:,.2f}")
        m2.metric("Mínimo Detectado", f"{min(precios_referencia):,.2f}")
        m3.metric("Máximo Detectado", f"{max(precios_referencia):,.2f}")
        st.divider()

    # 3. Estructura de Costos de Importación (Tu flujo de trabajo)
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📦 Costo de Importación")
        costo_fabrica = st.number_input("Costo de Fábrica (Origen)", min_value=0.0, step=0.01, value=5.00)
        gastos_import = st.number_input("Gastos de Importación y Aduana (%)", min_value=0.0, step=0.1, value=40.0)
        costo_cif_final = costo_fabrica * (1 + (gastos_import / 100))
        st.metric("Costo Unitario de Importación (CIF)", f"{costo_cif_final:,.2f}")

    with col2:
        st.subheader("📈 Margen y Estrategia")
        margen_deseado = st.slider("Margen de Utilidad Deseado (%)", 0, 100, 35)
        estrategia = st.selectbox("Estrategia (Kotler)", ["Basado en costo", "Paridad de mercado", "Descreme", "Penetración"])
        iva = st.checkbox("Incluir IVA Uruguay (22%)", value=True)

    # 4. Lógica de Cálculo
    precio_sin_iva = 0.0
    if estrategia == "Basado en costo":
        precio_sin_iva = costo_cif_final / (1 - (margen_deseado / 100)) if margen_deseado < 100 else costo_cif_final
    elif estrategia == "Paridad de mercado" and precios_referencia:
        precio_sin_iva = promedio_mkt
    elif estrategia == "Descreme" and precios_referencia:
        precio_sin_iva = max(precios_referencia) * 1.10
    elif estrategia == "Penetración" and precios_referencia:
        precio_sin_iva = min(precios_referencia) * 0.90
    else:
        precio_sin_iva = costo_cif_final / (1 - (margen_deseado / 100))

    precio_final = precio_sin_iva * 1.22 if iva else precio_sin_iva
    utilidad = precio_sin_iva - costo_cif_final
    margen_real = (utilidad / precio_sin_iva) * 100 if precio_sin_iva > 0 else 0

    # 5. Resultados y Exportación
    st.subheader("🎯 Resultado del Escenario")
    res1, res2, res3 = st.columns(3)
    res1.metric("Costo CIF Final", f"{costo_cif_final:,.2f}")
    res2.metric("PVP Sugerido (Final)", f"{precio_final:,.2f}")
    res3.metric("Margen Real Obtenido", f"{margen_real:.1f}%")

    if st.button("📥 GENERAR REPORTE EXCEL"):
        data_reporte = {
            "Concepto": ["Productos Analizados", "Estrategia", "Costo Fábrica", "Costo CIF", "Precio Sin IVA", "PVP Final", "Margen Real %", "Promedio Mercado"],
            "Valor": [", ".join(nombres_para_reporte), estrategia, costo_fabrica, costo_cif_final, precio_sin_iva, precio_final, f"{margen_real:.1f}%", promedio_mkt]
        }
        df_final = pd.DataFrame(data_reporte)
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_final.to_excel(writer, sheet_name='Escenario_Precio', index=False)
        
        st.download_button(
            label="💾 Descargar Análisis",
            data=output.getvalue(),
            file_name="Analisis_Precios_Wuerth.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
