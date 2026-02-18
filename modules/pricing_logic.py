import streamlit as st
import pandas as pd
from io import BytesIO

def mostrar_fijacion_precios():
    st.header("💰 Módulo de Fijación de Precios")
    
    precios_referencia = []
    nombres_referencia = []
    
    # 1. Sincronizar productos (Filtro Estricto de Descripción Corta)
    if 'resultados_investigacion' in st.session_state:
        with st.expander("📥 Sincronizar productos", expanded=True):
            df_invest = pd.DataFrame(st.session_state['resultados_investigacion'])
            
            # --- LIMPIEZA TOTAL DEL SELECTOR ---
            # Forzamos al sistema a usar 'Original (Würth)' que es tu dato del Excel.
            # Eliminamos cualquier rastro de la columna 'ADN Identificado' en la etiqueta.
            col_id = 'Original (Würth)' if 'Original (Würth)' in df_invest.columns else df_invest.columns[0]
            
            # Limpiamos la columna para asegurarnos de que solo tenga Código y Nombre Corto
            df_invest['etiqueta_limpia'] = df_invest[col_id].astype(str).str.split('\n').str[0]
            opciones = df_invest['etiqueta_limpia'].unique().tolist()
            
            seleccion_etiquetas = st.multiselect(
                "Busca por Código o Descripción Corta:", 
                options=opciones,
                help="Selecciona los artículos para evaluar sus escenarios de precios."
            )
            
            if st.button("Cargar Información de Mercado"):
                if seleccion_etiquetas:
                    df_filtrado = df_invest[df_invest['etiqueta_limpia'].isin(seleccion_etiquetas)]
                    
                    # Buscamos la columna de precios minoristas (P. Minorista)
                    col_precio = next((c for c in ['P. Minorista', 'Precio', 'precio_minorista'] if c in df_filtrado.columns), None)
                    
                    if col_precio:
                        precios_ref = pd.to_numeric(df_filtrado[col_precio], errors='coerce').dropna().tolist()
                        st.session_state['precios_sincronizados'] = precios_ref
                        st.session_state['nombres_sincronizados'] = seleccion_etiquetas
                        st.session_state['df_reporte_mkt'] = df_filtrado
                        st.success(f"✅ Se cargaron {len(precios_ref)} precios de competencia.")
                    else:
                        st.error("No se detectaron precios válidos. Revisa el módulo de investigación.")
                else:
                    st.warning("Selecciona al menos un producto.")

    if 'precios_sincronizados' in st.session_state:
        precios_referencia = st.session_state['precios_sincronizados']
        nombres_referencia = st.session_state.get('nombres_sincronizados', [])

    st.divider()

    # 2. Resumen de Competencia (Métricas para decidir tu Margen)
    promedio_mkt = 0
    if precios_referencia:
        st.subheader("📊 Resumen de Competencia en Uruguay")
        m1, m2, m3 = st.columns(3)
        promedio_mkt = sum(precios_referencia) / len(precios_referencia)
        m1.metric("Promedio Mercado", f"{promedio_mkt:,.2f}")
        m2.metric("Mínimo Detectado", f"{min(precios_referencia):,.2f}")
        m3.metric("Máximo Detectado", f"{max(precios_referencia):,.2f}")
        st.divider()

    # 3. Estructura de Costos de Importación (Tu flujo de trabajo diario)
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
            "Valor": [", ".join(nombres_referencia), estrategia, costo_fabrica, costo_cif_final, precio_sin_iva, precio_final, f"{margen_real:.1f}%", promedio_mkt]
        }
        df_final = pd.DataFrame(data_reporte)
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_final.to_excel(writer, sheet_name='Escenario_Precio', index=False)
            if 'df_reporte_mkt' in st.session_state:
                st.session_state['df_reporte_mkt'].to_excel(writer, sheet_name='Datos_Competencia', index=False)
        
        st.download_button(
            label="💾 Descargar Análisis",
            data=output.getvalue(),
            file_name="Analisis_Precios_Wuerth.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
