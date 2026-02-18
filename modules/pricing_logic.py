import streamlit as st
import pandas as pd

def mostrar_fijacion_precios():
    st.header("💰 Módulo de Fijación de Precios")
    
    # Inicialización de variables de estado para la sesión
    precios_referencia = []
    producto_seleccionado = "Ingreso Manual"
    
    # 1. INTERCONEXIÓN: Sincronización con Investigación de Mercado
    if 'resultados_investigacion' in st.session_state:
        with st.expander("📥 Sincronizar con Investigación de Mercado", expanded=True):
            df_invest = pd.DataFrame(st.session_state['resultados_investigacion'])
            
            # Selector para elegir el producto específico de la investigación
            lista_productos = df_invest['Original (Würth)'].unique().tolist()
            producto_seleccionado = st.selectbox("Selecciona el producto a analizar:", lista_productos)
            
            if st.button("Cargar Precios de este Producto"):
                # Filtrar resultados para el producto seleccionado
                df_filtrado = df_invest[df_invest['Original (Würth)'] == producto_seleccionado]
                
                # Búsqueda flexible de la columna de precios (evita KeyError)
                col_precio = None
                for c in ['P. Minorista', 'Precio', 'precio_minorista']:
                    if c in df_filtrado.columns:
                        col_precio = c
                        break
                
                if col_precio:
                    # Convertir a numérico y limpiar vacíos
                    precios_ref = pd.to_numeric(df_filtrado[col_precio], errors='coerce').dropna().tolist()
                    st.session_state['precios_sincronizados'] = precios_ref
                    st.session_state['nombre_prod_sinc'] = producto_seleccionado
                    st.success(f"✅ Se cargaron {len(precios_ref)} precios de competencia para este artículo.")
                else:
                    st.error("No se encontró una columna de precios válida en la investigación.")

    # Recuperar datos sincronizados de la sesión
    if 'precios_sincronizados' in st.session_state:
        precios_referencia = st.session_state['precios_sincronizados']
        producto_seleccionado = st.session_state.get('nombre_prod_sinc', "Sincronizado")

    st.divider()

    # 2. ESTRUCTURA DE COSTOS (CIF Uruguay)
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📦 Costo de Importación")
        costo_fabrica = st.number_input("Costo de Fábrica (Origen)", min_value=0.0, step=0.01, value=5.00)
        
        gastos_import = st.number_input("Gastos de Importación y Aduana (%)", 
                                        help="Tasas aduaneras, despachante y fletes de nacionalización",
                                        min_value=0.0, max_value=500.0, step=0.1, value=40.0)
        
        # Cálculo del Costo Unitario de Importación (CIF puesto en estante)
        costo_cif_final = costo_fabrica * (1 + (gastos_import / 100))
        st.metric("Costo Unitario de Importación (CIF)", f"{costo_cif_final:,.2f}")

    with col2:
        st.subheader("📈 Margen y Estrategia")
        margen_deseado = st.slider("Margen de Utilidad Deseado (%)", 0, 100, 35)
        
        estrategia = st.selectbox(
            "Seleccionar Estrategia (Kotler)",
            ["Basado en costo", "Paridad de mercado", "Descreme", "Penetración"]
        )
        
        iva = st.checkbox("Incluir IVA Uruguay (22%)", value=True)

    st.divider()

    # 3. LÓGICA DE CÁLCULO DE PRECIOS
    precio_sin_iva = 0.0
    error_estrategia = False

    if estrategia == "Basado en costo":
        # Fórmula de margen sobre precio de venta: Precio = Costo / (1 - Margen)
        precio_sin_iva = costo_cif_final / (1 - (margen_deseado / 100)) if margen_deseado < 100 else costo_cif_final
    
    elif estrategia == "Paridad de mercado":
        if precios_referencia:
            precio_sin_iva = sum(precios_referencia) / len(precios_referencia)
        else:
            error_estrategia = True
            
    elif estrategia == "Descreme":
        if precios_referencia:
            precio_sin_iva = max(precios_referencia) * 1.10
        else:
            error_estrategia = True
            
    elif estrategia == "Penetración":
        if precios_referencia:
            precio_sin_iva = min(precios_referencia) * 0.90
        else:
            error_estrategia = True

    # Si la estrategia elegida no tiene datos, volvemos a 'Basado en costo'
    if error_estrategia:
        st.warning(f"⚠️ La estrategia '{estrategia}' requiere datos de mercado. Usando 'Basado en costo' como respaldo.")
        precio_sin_iva = costo_cif_final / (1 - (margen_deseado / 100))

    # Cálculo final con IVA
    precio_final_publico = precio_sin_iva * 1.22 if iva else precio_sin_iva

    # 4. RESULTADOS FINALES
    st.subheader(f"🎯 Análisis de Precio: {producto_seleccionado}")
    res1, res2, res3 = st.columns(3)
    
    res1.metric("Costo CIF Final", f"{costo_cif_final:,.2f}")
    res2.metric("PVP Sugerido (Final)", f"{precio_final_publico:,.2f}")
    
    utilidad_neta = precio_sin_iva - costo_cif_final
    margen_real = (utilidad_neta / precio_sin_iva) * 100 if precio_sin_iva > 0 else 0
    res3.metric("Margen Real Obtenido", f"{margen_real:.1f}%")

    # Comparativa vs Mercado (Semáforo visual)
    if precios_referencia:
        promedio_mkt = sum(precios_referencia) / len(precios_referencia)
        diferencia = ((precio_sin_iva / promedio_mkt) - 1) * 100
        
        st.write("---")
        st.write("**Comparativa con la competencia seleccionada:**")
        if diferencia > 15:
            st.error(f"El precio sugerido está un {diferencia:.1f}% por encima del promedio de mercado.")
        elif diferencia < -15:
            st.warning(f"El precio sugerido está un {abs(diferencia):.1f}% por debajo del mercado. Revisar rentabilidad.")
        else:
            st.success(f"Precio competitivo (Diferencia de {diferencia:.1f}% respecto al promedio).")
            
        # Tabla detallada de precios usados para el cálculo
        with st.expander("Ver detalle de precios de competencia usados"):
            st.write(pd.DataFrame({"Precios de Competencia": precios_referencia}))
