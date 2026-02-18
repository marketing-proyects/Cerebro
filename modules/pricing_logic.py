import streamlit as st
import pandas as pd
from io import BytesIO

def mostrar_fijacion_precios():
    st.header("💰 Módulo de Fijación de Precios")
    
    precios_referencia = []
    nombres_para_reporte = []
    
    # 1. Sincronizar productos (Interfaz de Tabla con Columnas Independientes)
    if 'resultados_investigacion' in st.session_state:
        with st.expander("📥 Sincronizar productos", expanded=True):
            # Cargamos los resultados de la investigación
            df_invest = pd.DataFrame(st.session_state['resultados_investigacion'])
            
            # --- LIMPIEZA DE DATOS SEGURA ---
            # Identificamos la columna origen que contiene la info del Excel
            col_id = 'Original (Würth)' if 'Original (Würth)' in df_invest.columns else df_invest.columns[0]
            
            # Funciones de extracción robustas para evitar AttributeError
            def obtener_codigo(valor):
                texto = str(valor).strip()
                # El código es la primera palabra antes del primer espacio
                return texto.split(' ')[0] if ' ' in texto else texto

            def obtener_descripcion(valor):
                texto = str(valor).strip()
                # La descripción es todo lo que sigue al primer espacio, pero solo la primera línea
                # Esto ignora los párrafos largos de análisis de la IA
                linea_uno = texto.split('\n')[0]
                partes = linea_uno.split(' ', 1)
                return partes[1] if len(partes) > 1 else "Sin Descripción"

            # Creamos la tabla visual con columnas independientes
            df_visual = pd.DataFrame()
            df_visual['Código'] = df_invest[col_id].apply(obtener_codigo)
            df_visual['Descripción'] = df_invest[col_id].apply(obtener_descripcion)
            
            st.write("Selecciona los productos de tu Excel para el análisis de precios:")
            
            # Tabla interactiva (Respetando las columnas del Excel original)
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
                    # Obtenemos los códigos marcados en la tabla
                    codigos_elegidos = df_visual.iloc[filas_indices]['Código'].tolist()
                    
                    # Filtramos el origen buscando coincidencias exactas con el inicio del texto
                    df_filtrado = df_invest[df_invest[col_id].astype(str).str.startswith(tuple(codigos_elegidos))]
                    
                    # Buscamos la columna de precios minoristas (P. Minorista o Precio)
                    col_precio = next((c for c in ['P. Minorista', 'Precio', 'precio_minorista'] if c in df_filtrado.columns), None)
                    
                    if col_precio:
                        precios_ref = pd.to_numeric(df_filtrado[col_precio], errors='coerce').dropna().tolist()
                        st.session_state['precios_sincronizados'] = precios_ref
                        st.session_state['seleccion_nombres'] = df_visual.iloc[filas_indices]['Descripción'].tolist()
                        st.success(f"✅ Sincronizados {len(precios_ref)} precios de competencia.")
                    else:
                        st.error("No se detectaron precios válidos. Revisa el módulo de investigación.")
                else:
                    st.warning("Debes marcar al menos una fila en la tabla para proceder.")

    # Recuperar datos para el motor de cálculos
    if 'precios_sincronizados' in st.session_state:
        precios_referencia = st.session_state['precios_sincronizados']
        nombres_para_reporte = st.session_state.get('seleccion_nombres', [])

    st.divider()

    # 2. Resumen de Competencia (Lo que aporta valor para decidir el margen)
    promedio_mkt = 0
    if precios_referencia:
        st.subheader("📊 Indicadores de Mercado (Competencia)")
        m1, m2, m3 = st.columns(3)
        promedio_mkt = sum(precios_referencia) / len(precios_referencia)
        m1.metric("Promedio Mercado", f"{promedio_mkt:,.2f}")
        m2.metric("Mínimo Detectado", f"{min(precios_referencia):,.2f}")
        m3.metric("Máximo Detectado", f"{max(precios_referencia):,.2f}")
        st.divider()

    # 3. Estructura de Costos de Importación
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

    # 4. Lógica de Cálculo de Precios
    precio_sin_iva = 0.0
    if estrategia == "Basado en costo":
        # Fórmula: Precio = Costo / (1 - Margen)
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

    # 5. Resultados Finales
    st.subheader("🎯 Resultado del Escenario")
    res1, res2, res3 = st.columns(3)
    res1.metric("Costo CIF Final", f"{costo_cif_final:,.2f}")
    res2.metric("PVP Sugerido (Final)", f"{precio_final:,.2f}")
    res3.metric("Margen Real Obtenido", f"{margen_real:.1f}%")

    if st.button("📥 EXPORTAR ANÁLISIS A EXCEL"):
        data_reporte = {
            "Concepto": ["Productos Seleccionados", "Estrategia Usada", "Costo Fábrica", "Costo CIF Total", "Precio Neto (Sin IVA)", "PVP Público (Con IVA)", "Margen Obtenido %", "Promedio Mercado"],
            "Valor": [", ".join(nombres_para_reporte), estrategia, costo_fabrica, costo_cif_final, precio_sin_iva, precio_final, f"{margen_real:.1f}%", promedio_mkt]
        }
        df_final = pd.DataFrame(data_reporte)
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_final.to_excel(writer, sheet_name='Analisis_Precio', index=False)
        st.download_button("💾 Descargar Excel", output.getvalue(), "Analisis_Precios_Wuerth.xlsx")
