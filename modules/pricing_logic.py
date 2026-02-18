import streamlit as st
import pandas as pd

def mostrar_fijacion_precios():
    st.header("💰 Módulo de Fijación de Precios")
    
    precios_referencia = []
    
    # --- BLOQUE DE INTERCONEXIÓN SEGURO ---
    if 'resultados_investigacion' in st.session_state:
        with st.expander("📥 Datos de Investigación Disponibles", expanded=True):
            if st.button("Sincronizar Precios de Competencia"):
                df_invest = pd.DataFrame(st.session_state['resultados_investigacion'])
                
                # Buscamos la columna correcta para evitar el KeyError
                col_buscada = None
                for col in ['P. Minorista', 'Precio', 'precio_minorista']:
                    if col in df_invest.columns:
                        col_buscada = col
                        break
                
                if col_buscada:
                    precios_referencia = pd.to_numeric(df_invest[col_buscada], errors='coerce').dropna().tolist()
                    st.session_state['precios_sincronizados'] = precios_referencia
                    st.success(f"✅ Se cargaron {len(precios_referencia)} precios de referencia.")
                else:
                    st.error("No se encontró la columna de precios en los datos importados.")
    
    if 'precios_sincronizados' in st.session_state:
        precios_referencia = st.session_state['precios_sincronizados']

    st.divider()

    # --- ENTRADA DE COSTOS PRIVADOS ---
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
    if estrategia == "Cost-Plus (Margen Fijo)":
        precio_sugerido = costo_total / (1 - (margen_deseado / 100)) if margen_deseado < 100 else costo_total
    elif estrategia == "Paridad de Mercado" and precios_referencia:
        precio_sugerido = sum(precios_referencia) / len(precios_referencia)
    elif estrategia == "Descreme (Premium)" and precios_referencia:
        precio_sugerido = max(precios_referencia) * 1.10
    elif estrategia == "Penetración" and precios_referencia:
        precio_sugerido = min(precios_referencia) * 0.90
    else:
        precio_sugerido = costo_total / (1 - (margen_deseado / 100))

    precio_final = precio_sugerido * 1.22 if iva else precio_sugerido

    # --- RESULTADOS ---
    st.subheader("🎯 Resultado Final")
    res1, res2, res3 = st.columns(3)
    res1.metric("Costo Operativo", f"{costo_total:,.2f}")
    res2.metric("PVP Sugerido", f"{precio_final:,.2f}")
    margen_real = ((precio_sugerido - costo_total) / precio_sugerido) * 100 if precio_sugerido > 0 else 0
    res3.metric("Margen Neto Real", f"{margen_real:.1f}%")
