import streamlit as st
import pandas as pd
import io

def mostrar_matriz_decisiones():
    st.header("🎯 Matriz de Decisiones: Consola de Campañas")
    st.info("Diseñá tus ofertas partiendo de un 40% de margen. Bloqueá precios y gestioná tu campaña.")

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

    # Consolidación
    df_consolidado = pd.concat([df_stk, df_vto], ignore_index=True).drop_duplicates(subset=['Material'], keep='first')

    # --- 3. DISEÑADOR DE ACCIÓN ---
    st.divider()
    st.subheader("🧪 2. Diseñar Nueva Acción (Regla 40% GP)")
    
    options = df_consolidado['Descripción del material'].tolist()
    seleccionados = st.multiselect("Seleccioná artículos para esta acción:", options)

    if seleccionados:
        df_sb = df_consolidado[df_consolidado['Descripción del material'].isin(seleccionados)].copy()
        
        # REGLA DE ORO: Partimos del 40% de GP (Costo / 0.60)
        df_sb['Precio_Lista'] = df_sb['PFEP'] / 0.60
        df_sb['Precio_Promo'] = df_sb['Precio_Lista'] # Por defecto igual al de lista (40% GP)

        st.write("📝 **Ajustá únicamente los precios de Lista y Promo:**")
        df_ed = st.data_editor(
            df_sb[['Material', 'Descripción del material', 'PFEP', 'Precio_Lista', 'Precio_Promo', 'Indicador ABC']],
            column_config={
                "Material": st.column_config.TextColumn("Código", disabled=True),
                "Descripción del material": st.column_config.TextColumn("Descripción", disabled=True),
                "PFEP": st.column_config.NumberColumn("Costo", format="$ %.2f", disabled=True),
                "Indicador ABC": st.column_config.TextColumn("Cat", disabled=True),
                "Precio_Lista": st.column_config.NumberColumn("📖 P. LISTA", format="$ %.2f", help="Editable: Precio base para el % OFF."),
                "Precio_Promo": st.column_config.NumberColumn("💰 P. PROMO", format="$ %.2f", help="Editable: Precio final de oferta.")
            },
            hide_index=True, key="editor_diseno"
        )

        # Configuración de Campaña
        c1, c2 = st.columns(2)
        tipo = c1.selectbox("Tipo:", ["Oferta Individual", "Combo / Pack"])
        nombre = c2.text_input("Nombre de la Campaña:", placeholder="ej: Pack Frenos Sep")

        if st.button("➕ Añadir a la Propuesta Final", use_container_width=True, type="primary"):
            if not nombre:
                st.error("Ponle un nombre a la campaña para identificarla.")
            else:
                # Cálculos antes de guardar
                df_ed['Campaña'] = nombre
                df_ed['Tipo'] = tipo
                df_ed['$ OFF'] = df_ed['Precio_Lista'] - df_ed['Precio_Promo']
                df_ed['% OFF'] = (df_ed['$ OFF'] / df_ed['Precio_Lista']) * 100
                df_ed['GP%'] = ((df_ed['Precio_Promo'] - df_ed['PFEP']) / df_ed['Precio_Promo']) * 100
                
                st.session_state['propuesta_acumulada'] = pd.concat([st.session_state['propuesta_acumulada'], df_ed], ignore_index=True)
                st.toast(f"Añadido: {nombre}")
                st.rerun()

    # --- 4. GESTIÓN DE LA PROPUESTA FINAL (BORRAR Y EDITAR) ---
    if not st.session_state['propuesta_acumulada'].empty:
        st.divider()
        st.subheader("📋 3. Revisión y Gestión de Campañas")
        st.caption("Seleccioná filas y presioná 'Supr' o usá el ícono de papelera para eliminar errores.")

        # Usamos data_editor con num_rows="dynamic" para permitir ELIMINAR
        # Bloqueamos todo para que sea solo una tabla de gestión de filas
        df_actualizado = st.data_editor(
            st.session_state['propuesta_acumulada'],
            column_config={
                "Campaña": st.column_config.TextColumn("Campaña", disabled=True),
                "Material": st.column_config.TextColumn("Código", disabled=True),
                "Precio_Promo": st.column_config.NumberColumn("P. Promo", format="$ %.2f", disabled=True),
                "GP%": st.column_config.NumberColumn("GP%", format="%.1f%%", disabled=True),
                "% OFF": st.column_config.NumberColumn("% OFF", format="%.0f%%", disabled=True),
            },
            num_rows="dynamic", # <--- ESTO PERMITE BORRAR FILAS
            hide_index=True,
            use_container_width=True,
            key="gestor_final"
        )
        
        # Sincronizamos si el usuario borró algo
        if len(df_actualizado) != len(st.session_state['propuesta_acumulada']):
            st.session_state['propuesta_acumulada'] = df_actualizado
            st.rerun()

        # --- EXPORTACIÓN ---
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            # Hoja para Marketing (Limpia)
            df_mkt = df_actualizado[['Campaña', 'Tipo', 'Material', 'Descripción del material', 'Precio_Lista', 'Precio_Promo', '$ OFF', '% OFF']]
            df_mkt.to_excel(writer, index=False, sheet_name='PARA_DISENADOR')
            
            # Hoja para Finanzas (Con costos)
            df_actualizado.to_excel(writer, index=False, sheet_name='CONTROL_FINANCIERO')

        st.download_button(
            label="📥 DESCARGAR PACK DE CAMPAÑAS (Excel)",
            data=output.getvalue(),
            file_name="Marketing_Wurth_Consolidado.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
