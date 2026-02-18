import streamlit as st
import pandas as pd

def mostrar_fijacion_precios():
    st.header("💰 Módulo de Fijación de Precios")
    
    # 1. Inicializar lista de precios de referencia
    precios_referencia = []
    
    # --- BLOQUE DE INTERCONEXIÓN ---
    if 'resultados_investigacion' in st.session_state:
        with st.expander("📥 Datos de Investigación Disponibles", expanded=True):
            st.write("Se han detectado resultados de la investigación de mercado.")
            if st.button("Sincronizar Precios de Competencia"):
                df_invest = pd.DataFrame(st.session_state['resultados_investigacion'])
                # Filtramos solo valores numéricos válidos
                precios_referencia = pd.to_numeric(df_invest['Precio'], errors='coerce').dropna().tolist()
                st.session_state['precios_sincronizados'] = precios_referencia
                st.success(f"Se han cargado {len(precios_referencia)} precios de referencia.")
    
    # Recuperar precios sincronizados si existen en la sesión
    if 'precios_sincronizados' in st.session_state:
        precios_referencia = st.session_state['precios_sincronizados']

    st.divider()

    # 2. Entrada de Datos de Costos (Privado)
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🛠️ Estructura de Costos")
        costo_base = st.number_input("Costo de Importación (CIF) / Costo Base", min_value=0.0, step=1.0, value=100.0)
        gastos_op = st.number_input("Gastos Operativos y Logísticos (%)", min_value=0.0, max_value=100.0, step=1.0, value=15.0)
        iva = st.checkbox("Incluir IVA Uruguay (22%)", value=True)

    costo_total = costo_base * (1 + (gastos_op / 100))
    # El precio sugerido lo calculamos sin IVA y luego lo mostramos con/sin según se prefiera
    
    with col2:
        st.subheader("📈 Margen y Estrategia")
        margen_deseado = st.slider("Margen de Contribución Deseado (%)", 0, 100, 30)
        estrategia = st.selectbox(
            "Seleccionar Estrategia de Posicionamiento",
            ["Cost-Plus (Margen Fijo)", "Paridad de Mercado", "Descreme (Premium)", "Penetración"]
        )

    st.divider()

    # 3. Lógica de Cálculo de Precios
    precio_sugerido = 0.0
    detalles_estrategia = ""

    if estrategia == "Cost-Plus (Margen Fijo)":
        precio_sugerido = costo_total / (1 - (margen_deseado / 100)) if margen_deseado < 100 else costo_total
        detalles_estrategia = "Margen fijo sobre el costo total."
    
    elif estrategia == "Paridad de Mercado":
        if precios_referencia:
            precio_sugerido = sum(precios_referencia) / len(precios_referencia)
            detalles_estrategia = "Alineado al promedio de la competencia."
        else:
            st.error("No hay precios de referencia. Realiza una investigación primero.")

    elif estrategia == "Descreme (Premium)":
        if precios_referencia:
            precio_sugerido = max(precios_referencia) * 1.10
            detalles_estrategia = "10% por encima del competidor más caro."
        else:
            precio_sugerido = costo_total * 2
            detalles_estrategia = "Estrategia Premium (2x costo por defecto)."

    elif estrategia == "Penetración":
        if precios_referencia:
            precio_sugerido = min(precios_referencia) * 0.90
            detalles_estrategia = "10% por debajo del competidor más económico."
        else:
            precio_sugerido = costo_total * 1.10
            detalles_estrategia = "Margen de penetración mínimo (10%)."

    # Aplicar IVA si está marcado
    precio_final = precio_sugerido * 1.22 if iva else precio_sugerido

    # 4. Resultados Finales
    st.subheader("🎯 Resultado de la Simulación")
    res_col1, res_col2, res_col3 = st.columns(3)
    
    with res_col1:
        st.metric("Costo Total Operativo", f"{costo_total:,.2f}")
    
    with res_col2:
        st.metric("Precio Venta Final", f"{precio_final:,.2f}", 
                  delta=f"{(precio_final - (costo_total * 1.22 if iva else costo_total)):,.2f} utilidad")
    
    with res_col3:
        margen_real = ((precio_sugerido - costo_total) / precio_sugerido) * 100 if precio_sugerido > 0 else 0
        st.metric("Margen Real (Neto)", f"{margen_real:.1f}%")

    st.write(f"**Análisis:** {detalles_estrategia}")

    # Semáforo de Competitividad
    if precios_referencia and precio_sugerido > 0:
        promedio = sum(precios_referencia) / len(precios_referencia)
        dif = ((precio_sugerido / promedio) - 1) * 100
        if dif > 15: st.error(f"⚠️ Estás {dif:.1f}% arriba del promedio.")
        elif dif < -15: st.warning(f"💡 Estás {abs(dif):.1f}% debajo del promedio.")
        else: st.success("✅ Precio competitivo.")
