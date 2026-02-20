import streamlit as st
import pandas as pd
import io

def mostrar_matriz_decisiones():
    st.header("🎯 Matriz de Decisiones: Consola de Campañas")
    st.info("Diseñá múltiples acciones (Ofertas y Combos) en una sola sesión.")

    # --- 1. MEMORIA DE LA PROPUESTA ---
    if 'propuesta_acumulada' not in st.session_state:
        st.session_state['propuesta_acumulada'] = pd.DataFrame()

    # --- 2. RECUPERAR DATOS ---
    st.subheader("📥 1. Cargar Artículos de Análisis")
    c_btn1, c_btn2, c_btn3 = st.columns([1, 1, 1])
    with c_btn1:
        if st.button("🔄 Traer Vencimientos", use_container_width=True):
            if 'data_vencimientos' in st.session_state: st.toast("Vencimientos cargados")
            else: st.error("No hay datos")
    with c_btn2:
        if st.button("🔄 Traer Overstock", use_container_width=True):
            if 'data_overstock' in st.session_state: st.toast("Overstock cargado")
            else: st.error("No hay datos")
    with c_btn3:
        if st.button("🗑️ Limpiar Propuesta", type="secondary", use_container_width=True):
            st.session_state['propuesta_acumulada'] = pd.DataFrame()
            st.rerun()

    df_vto = st.session_state.get('data_vencimientos', pd.DataFrame())
    df_stk = st.session_state.get('data_overstock', pd.DataFrame())

    if df_vto.empty and df_stk.empty:
        st.warning("⚠️ El laboratorio está vacío. Procesá datos en Vencimientos u Overstock primero.")
        return

    # Consolidación
    if not df_vto.empty: df_vto['Alerta'] = "⏳ Vto"
    if not df_stk.empty: df_stk['Alerta'] = "💰 Stock"
    df_consolidado = pd.concat([df_stk, df_vto], ignore_index=True).drop_duplicates(subset=['Material'], keep='first')

    # --- 3. DISEÑADOR DE ACCIÓN ACTUAL ---
    st.divider()
    st.subheader("🧪 2. Diseñar Nueva Acción")
    
    with st.expander("Configurar Productos Seleccionados", expanded=True):
        options = df_consolidado['Descripción del material'].tolist()
        seleccionados = st.multiselect("Seleccioná los artículos para esta acción específica:", options)

        if seleccionados:
            df_sandbox = df_consolidado[df_consolidado['Descripción del material'].isin(seleccionados)].copy()
            
            # Inicialización de precios (GP 40%)
            df_sandbox['Precio_Lista'] = df_sandbox['PFEP'] / 0.60
            df_sandbox['Precio_Promo'] = df_sandbox['Precio_Lista'] * 0.90

            st.write("Ajustá Precios de Lista y Promo para esta selección:")
            df_editado = st.data_editor(
                df_sandbox[['Material', 'Descripción del material', 'PFEP', 'Precio_Lista', 'Precio_Promo']],
                column_config={
                    "PFEP": st.column_config.NumberColumn("Costo", disabled=True),
                    "Precio_Lista": st.column_config.NumberColumn("📖 P. LISTA", format="$ %.2f"),
                    "Precio_Promo": st.column_config.NumberColumn("💰 P. PROMO", format="$ %.2f"),
                },
                hide_index=True, key="editor_current"
            )

            # --- CONFIGURAR TIPO DE ACCIÓN ---
            c1, c2 = st.columns(2)
            tipo_accion = c1.radio("Tipo de Acción:", ["Ofertas Individuales", "Combo / Pack Agrupado"])
            nombre_accion = c2.text_input("Nombre de la Acción / Campaña:", placeholder="ej: Pack Mecánica 2024")

            if tipo_accion == "Combo / Pack Agrupado":
                precio_total_combo = st.number_input("Precio Final del Combo Completo ($):", value=float(df_editado['Precio_Promo'].sum()))
                # Prorrateamos el precio del combo para las métricas
                ratio = precio_total_combo / df_editado['Precio_Promo'].sum() if df_editado['Precio_Promo'].sum() > 0 else 1
                df_editado['Precio_Promo'] = df_editado['Precio_Promo'] * ratio

            if st.button("➕ Añadir a la Propuesta Final", use_container_width=True, type="primary"):
                if not nombre_accion:
                    st.error("Por favor, asigná un nombre a la acción.")
                else:
                    df_editado['Campaña'] = nombre_accion
                    df_editado['Tipo'] = tipo_accion
                    # Cálculos de marketing
                    df_editado['$ OFF'] = df_editado['Precio_Lista'] - df_editado['Precio_Promo']
                    df_editado['% OFF'] = (df_editado['$ OFF'] / df_editado['Precio_Lista']) * 100
                    df_editado['GP%'] = ((df_editado['Precio_Promo'] - df_editado['PFEP']) / df_editado['Precio_Promo']) * 100
                    
                    st.session_state['propuesta_acumulada'] = pd.concat([st.session_state['propuesta_acumulada'], df_editado], ignore_index=True)
                    st.success(f"Acción '{nombre_accion}' añadida correctamente.")
                    st.rerun()

    # --- 4. RESUMEN FINAL Y EXPORTACIÓN ---
    if not st.session_state['propuesta_acumulada'].empty:
        st.divider()
        st.subheader("📋 3. Propuesta Final Consolidada")
        
        df_final = st.session_state['propuesta_acumulada']
        
        # Mostrar tabla resumida para el usuario
        st.dataframe(
            df_final[['Campaña', 'Tipo', 'Material', 'Descripción del material', 'Precio_Lista', 'Precio_Promo', '$ OFF', '% OFF', 'GP%']],
            use_container_width=True, hide_index=True
        )

        # Métricas Globales
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Acciones", df_final['Campaña'].nunique())
        m2.metric("GP Promedio Total", f"{df_final['GP%'].mean():.1f}%")
        m3.metric("Ahorro Total Cliente", f"$ {df_final['$ OFF'].sum():,.0f}")

        # --- EXCEL PARA EL DISEÑADOR ---
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            # Hoja para el diseñador (Limpia y enfocada en Marketing)
            df_disenador = df_final[['Campaña', 'Tipo', 'Material', 'Descripción del material', 'Precio_Lista', 'Precio_Promo', '$ OFF', '% OFF']]
            df_disenador.to_excel(writer, index=False, sheet_name='PARA_DISENADOR')
            
            # Hoja técnica para control de margen
            df_final.to_excel(writer, index=False, sheet_name='CONTROL_FINANCIERO')
            
            # Formato estético para el diseñador
            workbook = writer.book
            worksheet = writer.sheets['PARA_DISENADOR']
            header_format = workbook.add_format({'bold': True, 'bg_color': '#D71920', 'font_color': 'white'})
            for col_num, value in enumerate(df_disenador.columns.values):
                worksheet.write(0, col_num, value, header_format)

        st.download_button(
            label="📥 DESCARGAR PACK DE CAMPAÑAS (Excel)",
            data=output.getvalue(),
            file_name="Campaña_Marketing_Wurth_Consolidada.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
