import streamlit as st
import pandas as pd

def mostrar_fijacion_precios():
    st.header("💰 Módulo de Fijación de Precios")
    
    precios_referencia = []
    items_seleccionados = []
    
    # 1. INTERCONEXIÓN: Sincronización Multiproducto (Tu nueva estrategia)
    if 'resultados_investigacion' in st.session_state:
        with st.expander("📥 Sincronizar Familia de Productos", expanded=True):
            df_invest = pd.DataFrame(st.session_state['resultados_investigacion'])
            
            # Ahora permitimos seleccionar múltiples productos a la vez (Multiselect)
            lista_nombres = df_invest['Original (Würth)'].unique().tolist()
            items_seleccionados = st.multiselect(
                "Selecciona los productos para evaluar como familia:", 
                options=lista_nombres,
                help="Puedes seleccionar varios productos similares para promediar la competencia de la familia completa."
            )
            
            if st.button("Cargar Precios de la Selección"):
                if items_seleccionados:
                    # Filtramos todos los productos seleccionados
                    df_filtrado = df_invest[df_invest['Original (Würth)'].isin(items_seleccionados)]
                    
                    # Identificación flexible de columna de precio
                    col_precio = next((c for c in ['P. Minorista', 'Precio', 'precio_minorista'] if c in df_filtrado.columns), None)
                    
                    if col_precio:
                        precios_ref = pd.to_numeric(df_filtrado[col_precio], errors='coerce').dropna().tolist()
                        st.session_state['precios_sincronizados'] = precios_ref
                        st.session_state['items_actuales'] = items_seleccionados
                        st.success(f"✅ Se cargaron {len(precios_ref)} puntos de precio de la familia seleccionada.")
                    else:
                        st.error("No se detectó columna de precios en la investigación.")
                else:
                    st.warning("Por favor, selecciona al menos un producto.")

    # Recuperar datos sincronizados
    if 'precios_sincronizados' in st.session_state:
        precios_referencia = st.session_state['precios_sincronizados']
        items_seleccionados = st.session_state.get('items_actuales', ["Ingreso Manual"])

    st.divider()

    # 2. ESTRUCTURA DE COSTOS
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📦 Costo de Importación")
        costo_fabrica = st.number_input("Costo de Fábrica (Origen)", min_value=0.0, step=0.01, value=5.00)
        gastos_import = st.number_input("Gastos de Importación y Aduana (%)", min_value=0.0, max_value=500.0, step=0.1, value=40.0)
        
        costo_cif_final = costo_fabrica * (1 + (gastos_import / 100))
        st.metric("Costo Unitario de Importación (CIF)", f"{costo_cif_final:,.2f}")

    with col2:
        st.subheader("📈 Margen y Estrategia")
        margen_deseado = st.slider("Margen de Utilidad Deseado (%)", 0, 100, 35)
        estrategia = st.selectbox(
            "Estrategia (Kotler)",
            ["Basado en costo", "Paridad de mercado", "Descreme", "Penetración"]
        )
        iva = st.checkbox("Incluir IVA Uruguay (22%)", value=True)

    st.divider()

    # 3. LÓGICA DE CÁLCULO
    precio_sin_iva = 0.0
    error_mkt = False

    if estrategia == "Basado en costo":
        precio_sin_iva = costo_cif_final / (1 - (margen_deseado / 100)) if margen_deseado < 100 else costo_cif_final
    elif estrategia == "Paridad de mercado" and precios_referencia:
        precio_sin_iva = sum(precios_referencia) / len(precios_referencia)
    elif estrategia == "Descreme" and precios_referencia:
        precio_sin_iva = max(precios_referencia) * 1.10
    elif estrategia == "Penetración" and precios_referencia:
        precio_sin_iva = min(precios_referencia) * 0.90
    else:
        if estrategia != "Basado en costo": error_mkt = True
        precio_sin_iva = costo_cif_final / (1 - (margen_deseado / 100))

    if error_mkt:
        st.warning(f"⚠️ La estrategia '{estrategia}' requiere datos de mercado. Usando 'Basado en costo'.")

    precio_final = precio_sin_iva * 1.22 if iva else precio_sin_iva

    # 4. RESULTADOS FINALES
    st.subheader("🎯 Análisis de Precio")
    if items_seleccionados:
        st.caption(f"Productos evaluados: {', '.join(items_seleccionados[:3])}...")

    res1, res2, res3 = st.columns(3)
    res1.metric("Costo CIF Final", f"{costo_cif_final:,.2f}")
    res2.metric("PVP Sugerido (Final)", f"{precio_final:,.2f}")
    
    utilidad = precio_sin_iva - costo_cif_final
    margen_real = (utilidad / precio_sin_iva) * 100 if precio_sin_iva > 0 else 0
    res3.metric("Margen Real Obtenido", f"{margen_real:.1f}%")

    # 5. SEMÁFORO DE FAMILIA
    if precios_referencia:
        promedio_familia = sum(precios_referencia) / len(precios_referencia)
        dif = ((precio_sin_iva / promedio_familia) - 1) * 100
        st.write("---")
        if dif > 15: st.error(f"⚠️ Estás {dif:.1f}% por encima del promedio de la familia.")
        elif dif < -15: st.warning(f"💡 Estás {abs(dif):.1f}% debajo de la familia.")
        else: st.success("✅ Precio competitivo respecto a la familia de productos.")
        
        with st.expander("Ver desglose de precios detectados para esta familia"):
            st.write(pd.DataFrame({"Competencia Detectada": precios_referencia}))
