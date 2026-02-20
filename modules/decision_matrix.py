import streamlit as st
import pandas as pd
import io

def mostrar_matriz_decisiones():
    st.header("🎯 Matriz de Decisiones: Laboratorio de Promociones")
    st.info("Diseñá ofertas individuales o Combos (Promos) cruzando artículos de Vencimientos y Overstock.")

    # 1. RECUPERAR DATOS
    st.subheader("📥 1. Recuperar Artículos Analizados")
    c_btn1, c_btn2 = st.columns(2)
    with c_btn1:
        if st.button("🔄 Traer Vencimientos", use_container_width=True):
            if 'data_vencimientos' in st.session_state: st.toast("Datos cargados!")
            else: st.error("No hay datos en Vencimientos.")
    with c_btn2:
        if st.button("🔄 Traer Overstock", use_container_width=True):
            if 'data_overstock' in st.session_state: st.toast("Datos cargados!")
            else: st.error("No hay datos en Overstock.")

    df_vto = st.session_state.get('data_vencimientos', pd.DataFrame())
    df_stk = st.session_state.get('data_overstock', pd.DataFrame())

    if df_vto.empty and df_stk.empty:
        st.warning("⚠️ Laboratorio vacío. Analice datos en los otros módulos primero.")
        return

    # Consolidación (Unión)
    if not df_vto.empty: df_vto['Alerta'] = "⏳ Vto"
    if not df_stk.empty: df_stk['Alerta'] = "💰 Stock"
    df_consolidado = pd.concat([df_stk, df_vto], ignore_index=True).drop_duplicates(subset=['Material'], keep='first')

    # 2. SELECCIÓN DE PRODUCTOS
    st.divider()
    st.subheader("🧪 2. Configuración de la Acción Comercial")
    
    options = df_consolidado['Descripción del material'].tolist()
    seleccionados = st.multiselect("Seleccioná los artículos que integran esta acción:", options)

    if seleccionados:
        df_sandbox = df_consolidado[df_consolidado['Descripción del material'].isin(seleccionados)].copy()
        
        # Inicializamos columnas si no existen
        if 'Precio_Lista' not in df_sandbox.columns:
            # Sugerimos un precio de lista base (GP 40%) pero es editable
            df_sandbox['Precio_Lista'] = df_sandbox['PFEP'] / 0.60
            df_sandbox['Precio_Promo'] = df_sandbox['Precio_Lista'] * 0.90 # 10% off inicial

        st.write("📝 **Ajustá los valores resaltados (Lista y Promo):**")
        
        # EDITOR MANUAL
        df_editado = st.data_editor(
            df_sandbox[['Material', 'Descripción del material', 'PFEP', 'Precio_Lista', 'Precio_Promo', 'ATP-quantity']],
            column_config={
                "Material": st.column_config.TextColumn("Código", disabled=True),
                "Descripción del material": st.column_config.TextColumn("Descripción", disabled=True),
                "PFEP": st.column_config.NumberColumn("Costo (PFEP)", format="$ %.2f", disabled=True),
                "ATP-quantity": st.column_config.NumberColumn("Stock Disp.", disabled=True),
                "Precio_Lista": st.column_config.NumberColumn("📖 PRECIO LISTA", format="$ %.2f", help="Precio del catálogo/referencia."),
                "Precio_Promo": st.column_config.NumberColumn("💰 PRECIO PROMO", format="$ %.2f", help="Precio final de la oferta.")
            },
            hide_index=True,
            use_container_width=True,
            key="editor_pro"
        )

        # 3. CÁLCULOS DINÁMICOS
        # Descuentos
        df_editado['Desc_Dinero'] = df_editado['Precio_Lista'] - df_editado['Precio_Promo']
        df_editado['Desc_Porcentaje'] = (df_editado['Desc_Dinero'] / df_editado['Precio_Lista']) * 100
        # GP Individual
        df_editado['GP_Ind'] = ((df_editado['Precio_Promo'] - df_editado['PFEP']) / df_editado['Precio_Promo']) * 100

        # --- SECCIÓN DE COMBO / PROMO CRUZADA ---
        st.write("---")
        es_combo = st.toggle("📦 **¿Convertir esta selección en un COMBO?**", help="Si activas esto, el sistema calculará la rentabilidad del paquete completo.")

        if es_combo:
            nombre_combo = st.text_input("Nombre de la Promo (ej. Pack Power Impacto):", "Combo Especial")
            
            c_costo = (df_editado['PFEP']).sum()
            c_lista = (df_editado['Precio_Lista']).sum()
            
            st.markdown(f"#### Configuración del Combo: {nombre_combo}")
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                precio_combo = st.number_input("Precio Total del Combo ($):", value=float(df_editado['Precio_Promo'].sum()), min_value=0.1)
            
            # Métricas del Combo
            gp_combo = ((precio_combo - c_costo) / precio_combo) * 100
            desc_combo = ((c_lista - precio_combo) / c_lista) * 100
            ahorro_combo = c_lista - precio_combo

            st.markdown(f"""
            > **Métricas del Pack:**
            > * 🏷️ **Ahorro para el cliente:** $ {ahorro_combo:,.2f} ({desc_combo:.1f}% OFF)
            > * 📈 **GP del Combo:** {gp_combo:.1f}%
            """)
            
            if gp_combo < 20: st.error("⚠️ El margen del combo es muy bajo (menor al 20%).")
            elif gp_combo >= 40: st.success("✅ Margen del combo saludable (40% o más).")

        # 4. MÉTRICAS TOTALES Y DESCARGA
        st.write("---")
        st.subheader("📊 Resumen para Marketing")
        
        m1, m2, m3 = st.columns(3)
        # Mostramos el % OFF más alto como "Gancho"
        max_off = df_editado['Desc_Porcentaje'].max()
        m1.metric("Gancho de Marketing", f"{max_off:.0f}% OFF")
        
        # Cash In: Consideramos que vendemos 1 unidad de cada uno por cada venta (o el stock total)
        # Para simplificar, calculamos sobre el stock total disponible
        total_venta = (df_editado['Precio_Promo'] * df_editado['ATP-quantity']).sum()
        m2.metric("Recuperación de Caja", f"$ {total_venta:,.0f}")
        
        gp_medio = df_editado['GP_Ind'].mean()
        m3.metric("GP Medio de la Acción", f"{gp_medio:.1f}%")

        # Botón de Descarga
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_editado.to_excel(writer, index=False, sheet_name='Propuesta')
        
        st.download_button(
            label="📥 Exportar Propuesta para Flyer / Ventas",
            data=output.getvalue(),
            file_name="Propuesta_Comercial_Wurth.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
