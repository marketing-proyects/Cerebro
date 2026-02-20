import streamlit as st
import pandas as pd
import io

def mostrar_matriz_decisiones():
    st.header("🎯 Matriz de Decisiones: Laboratorio Comercial")
    st.info("Centraliza los problemas de inventario para diseñar acciones comerciales.")

    # 1. BOTONES DE RECUPERACIÓN
    st.subheader("📥 Recuperar Análisis de Diagnóstico")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Recuperar Datos de Vencimientos", use_container_width=True):
            if 'data_vencimientos' in st.session_state:
                st.toast("Datos de Vencimientos cargados!")
            else:
                st.error("No hay análisis previo en Vencimientos.")
                
    with col2:
        if st.button("🔄 Recuperar Datos de Overstock", use_container_width=True):
            if 'data_overstock' in st.session_state:
                st.toast("Datos de Overstock cargados!")
            else:
                st.error("No hay análisis previo en Overstock.")

    # 2. CONSOLIDACIÓN DE DATOS (UNIÓN, NO INTERSECCIÓN)
    df_vto = st.session_state.get('data_vencimientos', pd.DataFrame())
    df_stk = st.session_state.get('data_overstock', pd.DataFrame())

    if df_vto.empty and df_stk.empty:
        st.warning("⚠️ El laboratorio está vacío. Primero analiza datos en los otros módulos.")
        return

    # Marcamos el origen para que el usuario sepa por qué el producto está ahí
    if not df_vto.empty: df_vto['Alerta'] = "⏳ Vto"
    if not df_stk.empty: df_stk['Alerta'] = "💰 Stock"

    # Consolidamos (Si un producto está en ambos, se queda con la info de stock que tiene el PFEP)
    df_consolidado = pd.concat([df_stk, df_vto], ignore_index=True).drop_duplicates(subset=['Material'], keep='first')

    # 3. EL SANDBOX CREATIVO
    st.divider()
    st.subheader("🧪 Diseño de la Oferta")
    
    # Parámetros Globales
    with st.sidebar:
        st.header("📈 Meta de Rentabilidad")
        gp_meta = st.slider("GP Mínimo Objetivo (%)", 0, 100, 20)
        st.write("---")
        st.caption("Fórmula de Margen Bruto (GP):")
        st.latex(r"GP(\%) = \frac{Promo - Costo}{Promo} \times 100")

    # Selección de productos para la "Acción"
    options = df_consolidado['Descripción del material'].tolist()
    seleccionados = st.multiselect("Seleccionar artículos para agrupar en esta acción:", options)

    if seleccionados:
        df_sandbox = df_consolidado[df_consolidado['Descripción del material'].isin(seleccionados)].copy()
        
        # Inicializamos el precio promo (25% de margen sobre PFEP si existe)
        if 'PFEP' in df_sandbox.columns:
            df_sandbox['Precio_Promo'] = df_sandbox['PFEP'] * 1.25
        else:
            df_sandbox['Precio_Promo'] = 0.0

        # EDITOR MANUAL (Aquí sucede la magia)
        st.write("📝 **Ajusta los precios manualmente para ver el impacto:**")
        df_editado = st.data_editor(
            df_sandbox[['Alerta', 'Material', 'Descripción del material', 'PFEP', 'ATP-quantity', 'Precio_Promo', 'Indicador ABC']],
            column_config={
                "PFEP": st.column_config.NumberColumn("Costo (PFEP)", format="$ %.2f", disabled=True),
                "ATP-quantity": st.column_config.NumberColumn("Stock", disabled=True),
                "Precio_Promo": st.column_config.NumberColumn("PRECIO PROMO", format="$ %.2f", min_value=0.1),
                "Alerta": st.column_config.TextColumn("Motivo", disabled=True)
            },
            hide_index=True,
            use_container_width=True
        )

        # CÁLCULOS
        df_editado['GP_Accion'] = ((df_editado['Precio_Promo'] - df_editado['PFEP']) / df_editado['Precio_Promo']) * 100
        df_editado['Total_Caja'] = df_editado['Precio_Promo'] * df_editado['ATP-quantity']
        
        # MÉTRICAS FINALES
        m1, m2, m3 = st.columns(3)
        gp_final = df_editado['GP_Accion'].mean()
        m1.metric("GP Medio Ponderado", f"{gp_final:.1f}%", 
                  delta=f"{gp_final - gp_meta:.1f}%", 
                  delta_color="normal" if gp_final >= gp_meta else "inverse")
        m2.metric("Cash-In Estimado", f"$ {df_editado['Total_Caja'].sum():,.0f}")
        
        costo_total = (df_editado['PFEP'] * df_editado['ATP-quantity']).sum()
        utilidad = df_editado['Total_Caja'].sum() - costo_total
        m3.metric("Utilidad Bruta (Pje)", f"$ {utilidad:,.0f}")

        # DESCARGA
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_editado.to_excel(writer, index=False, sheet_name='PropuestaComercial')
        
        st.download_button(
            label="📥 Exportar Propuesta Promocional en Excel",
            data=output.getvalue(),
            file_name="Propuesta_Estrategica_Wurth.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
