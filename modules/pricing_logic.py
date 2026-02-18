import streamlit as st
import pandas as pd

def mostrar_fijacion_precios():
    st.header("💰 Módulo de Fijación de Precios")
    
    precios_referencia = []
    producto_seleccionado = "Ingreso Manual"
    
    # 1. Sincronización con Investigación de Mercado
    if 'resultados_investigacion' in st.session_state:
        with st.expander("📥 Sincronizar con Investigación de Mercado", expanded=True):
            df_invest = pd.DataFrame(st.session_state['resultados_investigacion'])
            
            # Selector para elegir qué producto de la lista analizar
            lista_productos = df_invest['Original (Würth)'].unique().tolist()
            producto_seleccionado = st.selectbox("Selecciona el producto a analizar:", lista_productos)
            
            if st.button("Cargar Precios de este Producto"):
                # Filtramos precios del producto elegido
                df_filtrado = df_invest[df_invest['Original (Würth)'] == producto_seleccionado]
                
                # Buscamos la columna de precios de forma flexible para evitar KeyError
                col_precio = None
                for c in ['P. Minorista', 'Precio', 'precio_minorista']:
                    if c in df_filtrado.columns:
                        col_precio = c
                        break
                
                if col_precio:
                    precios_referencia = pd.to_numeric(df_filtrado[col_precio], errors='coerce').dropna().tolist()
                    st.session_state['precios_sincronizados'] = precios_referencia
                    st.success(f"✅ Precios de competencia cargados para: {producto_seleccionado}")
                else:
                    st.error("No se encontró la columna de precios en la investigación.")

    # Recuperar datos si ya fueron sincronizados
    if 'precios_sincronizados' in st.session_state:
        precios_referencia = st.session_state['precios_sincronizados']

    st.divider()

    # 2. Estructura de Costos de Importación (Simplificada)
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📦 Costo de Importación")
        costo_fabrica = st.number_input("Costo de Fábrica (Origen)", min_value=0.0, step=1.0, value=100.0)
        
        gastos_import = st.number_input("Gastos de Importación y Aduana (%)", 
                                        help="Tasas aduaneras, despachante, fletes y nacionalización",
                                        min_value=0.0, max_value=200.0, step=0.1, value=15.0)
        
        # Costo Unitario de Importación (CIF) - Puesto en Almacén
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

    # 3. Lógica de Cálculo de Precios
    precio_sin_iva = 0.0
    if estrategia == "Basado en costo":
        precio_sin_iva = costo_cif_final / (1 - (margen_deseado / 100)) if margen_deseado < 100 else costo_cif_final
    elif estrategia == "Paridad de mercado" and precios_referencia:
        precio_sin_iva = sum(precios_referencia) / len(precios_referencia)
    elif estrategia == "Descreme" and precios_referencia:
        precio_sin_iva = max(precios_referencia) * 1.10
    elif estrategia == "Penetración" and precios_referencia:
        precio_sin_iva = min(precios_referencia) * 0.90
    else:
        # Fallback si no hay datos de mercado
        precio_sin_iva = costo_cif_final / (1 - (margen_deseado / 100))

    precio_final_publico = precio_sin_iva * 1.22 if iva else precio_sin_iva

    # 4. Resultados Finales
    st.subheader(f"🎯 Análisis de Precio: {producto_seleccionado}")
    res1, res2, res3 = st.columns(3)
    
    res1.metric("Costo CIF Final", f"{costo_cif_final:,.2f}")
    res2.metric("PVP Sugerido (Final)", f"{precio_final_publico:,.2f}")
    
    utilidad_neta = precio_sin_iva - costo_cif_final
    margen_real = (utilidad_neta / precio_sin_iva) * 100 if precio_sin_iva > 0 else 0
    res3.metric("Margen Real Obtenido", f"{margen_real:.1f}%")

    # Comparativa vs Mercado (Semáforo)
    if precios_referencia:
        promedio_mkt = sum(precios_referencia) / len(precios_referencia)
        diferencia = ((precio_sin_iva / promedio_mkt) - 1) * 100
        
        if diferencia > 15:
            st.error(f"⚠️ El precio está un {diferencia:.1f}% por encima del mercado.")
        elif diferencia < -15:
            st.warning(f"💡 El precio está un {abs(diferencia):.1f}% por debajo del mercado.")
        else:
            st.success(f"✅ Precio competitivo respecto al promedio uruguayo.")
