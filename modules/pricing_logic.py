import streamlit as st
import pandas as pd

def mostrar_fijacion_precios():
    st.header("💰 Módulo de Fijación de Precios")
    
    precios_referencia = []
    
    if 'resultados_investigacion' in st.session_state:
        with st.expander("📥 Datos de Investigación Disponibles", expanded=True):
            st.write("Se han detectado resultados multicompetidor.")
            if st.button("Sincronizar Precios de Competencia"):
                df_invest = pd.DataFrame(st.session_state['resultados_investigacion'])
                
                # CORRECCIÓN: Buscamos 'P. Minorista' que es el nombre en el nuevo reporte
                col_precio = 'P. Minorista' if 'P. Minorista' in df_invest.columns else 'Precio'
                
                if col_precio in df_invest.columns:
                    precios_referencia = pd.to_numeric(df_invest[col_precio], errors='coerce').dropna().tolist()
                    st.session_state['precios_sincronizados'] = precios_referencia
                    st.success(f"✅ {len(precios_referencia)} precios minoristas sincronizados.")
                else:
                    st.error("No se encontró la columna de precios en los resultados.")
    
    if 'precios_sincronizados' in st.session_state:
        precios_referencia = st.session_state['precios_sincronizados']

    st.divider()

    # --- ENTRADA DE COSTOS ---
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🛠️ Estructura de Costos")
        costo_base = st.number_input("Costo de Importación (CIF)", min_value=0.0, step=1.0, value=100.0)
        gastos_op = st.number_input("Gastos Operativos (%)", min_value=0.0, max_value=100.0, step=1.0, value=15.0)
        iva = st.checkbox("Incluir IVA Uruguay (22%)", value=True)

    costo_total = costo_base * (1 + (gastos_op / 100))
    
    with col2:
        st.subheader("📈 Margen y Estrategia")
        margen_deseado = st.slider("Margen Neto Deseado (%)", 0, 100, 30)
        estrategia = st.selectbox(
            "Estrategia de Posicionamiento",
            ["Cost-Plus (Margen Fijo)", "Paridad de Mercado", "Descreme (Premium)", "Penetración"]
        )

    st.divider()

    # --- LÓGICA DE PRECIOS ---
    precio_sugerido = 0.0
    detalles = ""

    if estrategia == "Cost-Plus (Margen Fijo)":
        precio_sugerido = costo_total / (1 - (margen_deseado / 100)) if margen_deseado < 100 else costo_total
        detalles = "Basado exclusivamente en tu margen interno."
    elif estrategia == "Paridad de Mercado" and precios_referencia:
        precio_sugerido = sum(precios_referencia) / len(precios_referencia)
        detalles = "Alineado al promedio de la competencia uruguaya."
    elif estrategia == "Descreme (Premium)" and precios_referencia:
        precio_sugerido = max(precios_referencia) * 1.10
        detalles = "Posicionamiento 10% arriba del máximo competidor."
    elif estrategia == "Penetración" and precios_referencia:
        precio_sugerido = min(precios_referencia) * 0.90
        detalles = "Precio agresivo 10% debajo del más barato."
    else:
        # Fallback si no hay precios de referencia
        precio_sugerido = costo_total / (1 - (margen_deseado / 100))
        if estrategia != "Cost-Plus (Margen Fijo)":
            st.warning("Usando Cost-Plus por falta de datos de competencia.")

    precio_final = precio_sugerido * 1.22 if iva else precio_sugerido

    # --- RESULTADOS ---
    st.subheader("🎯 Resultado Final")
    res1, res2, res3 = st.columns(3)
    res1.metric("Costo Operativo", f"{costo_total:,.2f}")
    res2.metric("PVP Sugerido", f"{precio_final:,.2f}")
    margen_real = ((precio_sugerido - costo_total) / precio_sugerido) * 100 if precio_sugerido > 0 else 0
    res3.metric("Margen Neto Real", f"{margen_real:.1f}%")

    if precios_referencia:
        promedio = sum(precios_referencia) / len(precios_referencia)
        dif = ((precio_sugerido / promedio) - 1) * 100
        if dif > 15: st.error(f"⚠️ {dif:.1f}% sobre el mercado.")
        elif dif < -15: st.warning(f"💡 {abs(dif):.1f}% bajo el mercado.")
        else: st.success("✅ Precio altamente competitivo.")
