import streamlit as st
import pandas as pd
import io

def mostrar_matriz_decisiones():
    st.header("🎯 Matriz de Decisiones: Laboratorio Comercial")
    st.info("Diseño de ofertas y acciones de marketing basadas en rentabilidad.")

    # 1. RECUPERAR DATOS
    st.subheader("📥 Recuperar Análisis de Diagnóstico")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Recuperar Datos de Vencimientos", use_container_width=True):
            if 'data_vencimientos' in st.session_state:
                st.toast("Datos de Vencimientos cargados!")
            else: st.error("No hay análisis previo en Vencimientos.")
    with col2:
        if st.button("🔄 Recuperar Datos de Overstock", use_container_width=True):
            if 'data_overstock' in st.session_state:
                st.toast("Datos de Overstock cargados!")
            else: st.error("No hay análisis previo en Overstock.")

    df_vto = st.session_state.get('data_vencimientos', pd.DataFrame())
    df_stk = st.session_state.get('data_overstock', pd.DataFrame())

    if df_vto.empty and df_stk.empty:
        st.warning("⚠️ El laboratorio está vacío. Analice datos en los otros módulos primero.")
        return

    # Consolidación
    if not df_vto.empty: df_vto['Alerta'] = "⏳ Vto"
    if not df_stk.empty: df_stk['Alerta'] = "💰 Stock"
    df_consolidado = pd.concat([df_stk, df_vto], ignore_index=True).drop_duplicates(subset=['Material'], keep='first')

    # 2. EL SANDBOX CREATIVO
    st.divider()
    st.subheader("🧪 Diseño de la Oferta y Marketing")
    
    with st.sidebar:
        st.header("📈 Meta de Rentabilidad")
        gp_meta = st.slider("GP Mínimo Objetivo (%)", 0, 100, 40)
        st.write("---")
        st.caption("Fórmula de Margen Bruto (GP):")
        st.latex(r"GP(\%) = \frac{Promo - Costo}{Promo} \times 100")

    options = df_consolidado['Descripción del material'].tolist()
    seleccionados = st.multiselect("Seleccionar artículos para la campaña:", options)

    if seleccionados:
        df_sandbox = df_consolidado[df_consolidado['Descripción del material'].isin(seleccionados)].copy()
        
        # PRECIO BASE (Precio de Lista que defiende el 40% GP)
        if 'PFEP' in df_sandbox.columns:
            df_sandbox['Precio_Base'] = df_sandbox['PFEP'] / 0.60
            # Iniciamos el Precio Promo igual al Base para que el usuario empiece a rebajar
            df_sandbox['Precio_Promo'] = df_sandbox['Precio_Base']
        else:
            st.error("Columna PFEP no encontrada.")
            return

        st.write("📝 **Ajusta el PRECIO PROMO. El sistema calculará los descuentos para el flyer:**")
        
        # EDITOR MANUAL
        df_editado = st.data_editor(
            df_sandbox[['Alerta', 'Material', 'Descripción del material', 'PFEP', 'Precio_Base', 'Precio_Promo', 'ATP-quantity']],
            column_config={
                "Alerta": st.column_config.TextColumn("Motivo", disabled=True),
                "Material": st.column_config.TextColumn("Código", disabled=True),
                "Descripción del material": st.column_config.TextColumn("Descripción", disabled=True),
                "PFEP": st.column_config.NumberColumn("Costo (PFEP)", format="$ %.2f", disabled=True),
                "Precio_Base": st.column_config.NumberColumn("Precio Sugerido (40% GP)", format="$ %.2f", disabled=True),
                "ATP-quantity": st.column_config.NumberColumn("Stock", disabled=True),
                "Precio_Promo": st.column_config.NumberColumn(
                    "💰 PRECIO PROMO", 
                    format="$ %.2f", 
                    min_value=0.1,
                    help="Ingresá aquí el precio de oferta."
                )
            },
            hide_index=True,
            use_container_width=True,
            key="editor_marketing"
        )

        # 3. CÁLCULOS PARA MARKETING Y FINANZAS
        # GP de la acción
        df_editado['GP_Accion'] = ((df_editado['Precio_Promo'] - df_editado['PFEP']) / df_editado['Precio_Promo']) * 100
        
        # Datos para el Flyer
        df_editado['Descuento_Dinero'] = df_editado['Precio_Base'] - df_editado['Precio_Promo']
        df_editado['Descuento_Porcentual'] = (df_editado['Descuento_Dinero'] / df_editado['Precio_Base']) * 100
        
        # Recuperación de Caja
        df_editado['Cash_In'] = df_editado['Precio_Promo'] * df_editado['ATP-quantity']

        # MÉTRICAS
        st.markdown("---")
        st.subheader("📊 Resultados de la Campaña")
        m1, m2, m3 = st.columns(3)
        
        gp_final = df_editado['GP_Accion'].mean()
        m1.metric("GP Medio Ponderado", f"{gp_final:.1f}%", 
                  delta=f"{gp_final - gp_meta:.1f}% vs Meta", 
                  delta_color="normal" if gp_final >= gp_meta else "inverse")
        
        m2.metric("Total Cash-In (Venta)", f"$ {df_editado['Cash_In'].sum():,.0f}")
        
        ahorro_total = df_editado['Descuento_Dinero'].sum()
        m3.metric("Ahorro Total p/ Clientes", f"$ {ahorro_total:,.0f}", help="Suma de todos los descuentos otorgados.")

        # TABLA PARA MARKETING
        st.write("🚀 **Datos listos para Diseño/Marketing:**")
        cols_flyer = ['Material', 'Descripción del material', 'Precio_Promo', 'Descuento_Dinero', 'Descuento_Porcentual']
        df_flyer = df_editado[cols_flyer].copy()
        
        # Formateo visual
        df_flyer['Descuento_Porcentual'] = df_flyer['Descuento_Porcentual'].map("{:.0f}% OFF".format)
        st.table(df_flyer)

        # DESCARGA COMPLETA
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_editado.to_excel(writer, index=False, sheet_name='Propuesta_Completa')
        
        st.download_button(
            label="📥 Exportar Propuesta en Excel",
            data=output.getvalue(),
            file_name="Campaña_Marketing_Wurth.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
