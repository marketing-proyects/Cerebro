import streamlit as st
import pandas as pd

def mostrar_fijacion_precios():
    st.header("💰 Módulo de Fijación de Precios")
    st.info("Este módulo permite calcular precios finales basados en diferentes estrategias de marketing, de forma privada y segura.")

    # 1. Recuperar datos de la investigación previa (Si existen)
    precios_referencia = []
    if 'resultados_investigacion' in st.session_state and st.session_state['resultados_investigacion']:
        st.subheader("📊 Referencias del Mercado (Investigación Previa)")
        df_investigacion = pd.DataFrame(st.session_state['resultados_investigacion'])
        
        # Mostrar una tabla resumida de la competencia para referencia
        st.dataframe(df_investigacion[['Original (Würth)', 'Competidor', 'Precio', 'Moneda', 'Calidad']])
        
        # Extraer el precio promedio para cálculos automáticos
        precios_referencia = df_investigacion['Precio'].tolist()
    else:
        st.warning("No se encontraron datos de investigación previa. Puedes ingresar los precios de competencia manualmente.")

    st.divider()

    # 2. Entrada de Datos de Costos (Privado)
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🛠️ Estructura de Costos")
        costo_base = st.number_input("Costo de Importación (CIF) / Costo Base", min_value=0.0, step=1.0, value=100.0)
        gastos_op = st.number_input("Gastos Operativos y Logísticos (%)", min_value=0.0, max_value=100.0, step=1.0, value=15.0)
        iva = st.checkbox("Incluir IVA Uruguay (22%)", value=True)

    # Cálculo del Costo Total
    costo_total = costo_base * (1 + (gastos_op / 100))
    if iva:
        costo_total_con_iva = costo_total * 1.22
    else:
        costo_total_con_iva = costo_total

    with col2:
        st.subheader("📈 Margen y Estrategia")
        margen_deseado = st.slider("Margen de Contribución Deseado (%)", 0, 100, 30)
        
        # Selector de Estrategia de Marketing
        estrategia = st.selectbox(
            "Seleccionar Estrategia de Posicionamiento",
            ["Cost-Plus (Margen Fijo)", "Paridad de Mercado", "Descreme (Premium)", "Penetración"]
        )

    st.divider()

    # 3. Lógica de Cálculo de Precios (Sin IA)
    precio_sugerido = 0.0
    detalles_estrategia = ""

    if estrategia == "Cost-Plus (Margen Fijo)":
        precio_sugerido = costo_total / (1 - (margen_deseado / 100))
        detalles_estrategia = "Calculado sumando el margen deseado directamente sobre el costo total."
    
    elif estrategia == "Paridad de Mercado":
        if precios_referencia:
            precio_sugerido = sum(precios_referencia) / len(precios_referencia)
            detalles_estrategia = "Precio alineado al promedio detectado en la competencia uruguaya."
        else:
            precio_sugerido = 0.0
            st.error("No hay precios de referencia para usar esta estrategia.")

    elif estrategia == "Descreme (Premium)":
        if precios_referencia:
            precio_sugerido = max(precios_referencia) * 1.10
            detalles_estrategia = "Precio posicionado un 10% por encima del líder para resaltar exclusividad."
        else:
            precio_sugerido = costo_total * 2
            detalles_estrategia = "Posicionamiento de alto valor (Default 2x costo)."

    elif estrategia == "Penetración":
        if precios_referencia:
            precio_sugerido = min(precios_referencia) * 0.90
            detalles_estrategia = "Precio agresivo (10% debajo del mínimo) para capturar cuota de mercado rápido."
        else:
            precio_sugerido = costo_total * 1.10
            detalles_estrategia = "Margen mínimo sugerido para entrada al mercado."

    # 4. Resultados Finales
    st.subheader("🎯 Resultado de la Simulación")
    
    res_col1, res_col2, res_col3 = st.columns(3)
    
    with res_col1:
        st.metric("Costo Total (inc. Gastos)", f"{costo_total:,.2f}")
    
    with res_col2:
        st.metric("Precio Venta Sugerido", f"{precio_sugerido:,.2f}", 
                  delta=f"{(precio_sugerido - costo_total):,.2f} utilidad")
    
    with res_col3:
        margen_real = ((precio_sugerido - costo_total) / precio_sugerido) * 100 if precio_sugerido > 0 else 0
        st.metric("Margen Real Obtenido", f"{margen_real:.1f}%")

    st.write(f"**Análisis de la Estrategia:** {detalles_estrategia}")

    # Semáforo de Competitividad
    if precios_referencia and precio_sugerido > 0:
        promedio = sum(precios_referencia) / len(precios_referencia)
        diferencia = ((precio_sugerido / promedio) - 1) * 100
        
        if diferencia > 15:
            st.error(f"⚠️ Tu precio está un {diferencia:.1f}% por encima del promedio de mercado. Riesgo de baja rotación.")
        elif diferencia < -15:
            st.warning(f"💡 Tu precio está un {abs(diferencia):.1f}% por debajo del mercado. Estás sacrificando margen.")
        else:
            st.success(f"✅ Tu precio es competitivo (Diferencia de {diferencia:.1f}% vs mercado).")
