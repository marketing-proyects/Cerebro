import streamlit as st
import pandas as pd
import io

def mostrar_matriz_decisiones():
    st.header("🎯 Matriz de Decisiones: Consola de Campañas")
    st.info("Diseñá tus ofertas: Lista (x2.5 PFEP) y Promo (Piso 40% GP). Ambos campos son editables.")

    # --- 1. MEMORIA DE LA PROPUESTA ---
    if 'propuesta_acumulada' not in st.session_state:
        st.session_state['propuesta_acumulada'] = pd.DataFrame()

    # --- 2. RECUPERAR DATOS ---
    st.subheader("📥 1. Cargar Artículos de Análisis")
    c_btn1, c_btn2, c_btn3 = st.columns([1, 1, 1])
    with c_btn1:
        if st.button("🔄 Traer Vencimientos", use_container_width=True):
            if 'data_vencimientos' in st.session_state: st.toast("Vencimientos cargados")
            else: st.error("No hay datos previos")
    with c_btn2:
        if st.button("🔄 Traer Overstock", use_container_width=True):
            if 'data_overstock' in st.session_state: st.toast("Overstock cargado")
            else: st.error("No hay datos previos")
    with c_btn3:
        if st.button("🗑️ Vaciar Todo", type="secondary", use_container_width=True):
            st.session_state['propuesta_acumulada'] = pd.DataFrame()
            st.rerun()

    df_vto = st.session_state.get('data_vencimientos', pd.DataFrame())
    df_stk = st.session_state.get('data_overstock', pd.DataFrame())

    if df_vto.empty and df_stk.empty:
        st.warning("⚠️ Laboratorio vacío. Analizá datos en Vencimientos u Overstock primero.")
        return

    # Consolidación de datos maestros
    df_consolidado = pd.concat([df_stk, df_vto], ignore_index=True).drop_duplicates(subset=['Material'], keep='first')

    # --- 3. DISEÑADOR DE ACCIÓN ---
    st.divider()
    st.subheader("🧪 2. Diseñar Nueva Acción")
    
    options = df_consolidado['Descripción del material'].tolist()
    seleccionados = st.multiselect("Seleccioná artículos para esta acción:", options)

    if seleccionados:
        df_sb = df_consolidado[df_consolidado['Descripción del material'].isin(seleccionados)].copy()
        
        # --- NUEVA LÓGICA DE PRECIOS ---
        # Precio Lista: x2.5 del costo (60% GP inicial)
        df_sb['Precio_Lista'] = df_sb['PFEP'] * 2.5
        # Precio Promo: Piso de 40% GP (Costo / 0.6)
        df_sb['Precio_Promo'] = df_sb['PFEP'] / 0.60

        st.write("📝 **Editá Lista y Promo (Campos resaltados):**")
        df_ed = st.data_editor(
            df_sb[['Material', 'Descripción del material', 'PFEP', 'Precio_Lista', 'Precio_Promo', 'Indicador ABC', 'ATP-quantity']],
            column_config={
                "Material": st.column_config.TextColumn("Código", disabled=True),
                "Descripción del material": st.column_config.TextColumn("Descripción", disabled=True),
                "PFEP": st.column_config.NumberColumn("Costo (PFEP)", format="$ %.2f", disabled=True),
                "Indicador ABC": st.column_config.TextColumn("Cat", disabled=True),
                "ATP-quantity": st.column_config.NumberColumn("Stock", disabled=True),
                # CAMPOS EDITABLES
                "Precio_Lista": st.column_config.NumberColumn("📖 P. LISTA (x2.5)", format="$ %.2f", help="Precio de catálogo sugerido."),
                "Precio_Promo": st.column_config.NumberColumn("💰 P. PROMO (40%)", format="$ %.2f", help="Piso preaprobado de oferta.")
            },
            hide_index=True, key="editor_diseno_v2"
        )

        # Configuración de Campaña
        c1, c2 = st.columns(2)
        tipo = c1.selectbox("Tipo de Acción:", ["Oferta Individual", "Combo / Pack Agrupado"])
        nombre = c2.text_input("Nombre de la Campaña:", placeholder="ej: Promo Herramientas Impacto")

        if st.button("➕ Añadir a la Propuesta Final", use_container_width=True, type="primary"):
            if not nombre:
                st.error("Debes asignar un nombre a la campaña.")
            else:
                # Cálculos de marketing y finanzas
                df_ed['Campaña'] = nombre
                df_ed['Tipo'] = tipo
                df_ed['$ OFF'] = df_ed['Precio_Lista'] - df_ed['Precio_Promo']
                df_ed['% OFF'] = (df_ed['$ OFF'] / df_ed['Precio_Lista']) * 100
                df_ed['GP%'] = ((df_ed['Precio_Promo'] - df_ed['PFEP']) / df_ed['Precio_Promo']) * 100
                
                # Acumulamos en la sesión
                st.session_state['propuesta_acumulada'] = pd.concat([st.session_state['propuesta_acumulada'], df_ed], ignore_index=True)
                st.toast(f"Añadido: {nombre}")
                st.rerun()

    # --- 4. GESTIÓN Y ELIMINACIÓN DE LA PROPUESTA ---
    if not st.session_state['propuesta_acumulada'].empty:
        st.divider()
        st.subheader("📋 3. Revisión de Campañas Acumuladas")
        st.caption("Seleccioná filas y usá la papelera o 'Supr' para eliminar errores o duplicados.")

        # Editor dinámico para permitir borrado
        df_actualizado = st.data_editor(
            st.session_state['propuesta_acumulada'],
            column_config={
                "Campaña": st.column_config.TextColumn("Campaña", disabled=True),
                "Material": st.column_config.TextColumn("Código", disabled=True),
                "Precio_Lista": st.column_config.NumberColumn("P. Lista", format="$ %.2f", disabled=True),
                "Precio_Promo": st.column_config.NumberColumn("P. Promo", format="$ %.2f", disabled=True),
                "GP%": st.column_config.NumberColumn("GP%", format="%.1f%%", disabled=True),
                "% OFF": st.column_config.NumberColumn("% OFF", format="%.0f%%", disabled=True),
            },
            num_rows="dynamic", # Habilita borrar filas
            hide_index=True,
            use_container_width=True,
            key="gestor_final_v2"
        )
        
        # Sincronización si se eliminaron filas
        if len(df_actualizado) != len(st.session_state['propuesta_acumulada']):
            st.session_state['propuesta_acumulada'] = df_actualizado
            st.rerun()

        # Métricas Consolidadas
        st.markdown("---")
        m1, m2, m3 = st.columns(3)
        m1.metric("Caja Recuperable (Total)", f"$ {df_actualizado['Precio_Promo'].mul(df_actualizado['ATP-quantity']).sum():,.0f}")
        m2.metric("GP Promedio", f"{df_actualizado['GP%'].mean():.1f}%")
        m3.metric("Campañas Activas", df_actualizado['Campaña'].nunique())

        # --- EXPORTACIÓN ---
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            # Hoja Marketing
            df_mkt = df_actualizado[['Campaña', 'Tipo', 'Material', 'Descripción del material', 'Precio_Lista', 'Precio_Promo', '$ OFF', '% OFF']]
            df_mkt.to_excel(writer, index=False, sheet_name='DISEÑO_MARKETING')
            # Hoja Finanzas
            df_actualizado.to_excel(writer, index=False, sheet_name='CONTROL_RENTABILIDAD')

        st.download_button(
            label="📥 DESCARGAR PROPUESTAS CONSOLIDADAS",
            data=output.getvalue(),
            file_name="Propuesta_Comercial_Wurth.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
