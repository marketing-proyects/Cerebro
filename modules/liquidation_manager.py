import streamlit as st
import pandas as pd
import re
import io

def mostrar_modulo_liquidation():
    st.header("📦 Módulo de Análisis Estratégico / Próximos Vencimientos")
    st.info("Diagnóstico de Inventario por Lote y Unidad de Empaque (UE).")

    # 1. Glosario Técnico (Unificado con Overstock)
    with st.expander("ℹ️ VER LEYENDA TÉCNICA (Rotación ABC/DEFG)"):
        st.markdown("""
        | Cat | Comportamiento del Capital | Estrategia ante Vencimiento |
        | :--- | :--- | :--- |
        | **A / B** | **Consumibles Críticos:** Salen solos. | No requiere grandes descuentos. |
        | **C / D** | **Insumos y Maquinaria:** Salida moderada. | Ofertas de volumen (Combos). |
        | **E / F** | **Artículos Técnicos:** Salida lenta. | Prioridad en acciones dirigidas. |
        | **G** | **Inactivos / Outlet:** Máximo riesgo. | **Liquidación Total:** Precio de costo. |
        | **N** | **Lanzamientos:** Sin historial. | Monitorear tracción inicial. |
        """)

    archivo = st.file_uploader("Cargar volcado de Vencimientos", type=['xlsx', 'csv'], key="liq_uploader_v_final")

    if archivo:
        try:
            # --- 1. LECTURA ---
            df = pd.read_csv(archivo) if archivo.name.endswith('.csv') else pd.read_excel(archivo)
            df.columns = df.columns.str.strip()

            # --- 2. LIMPIEZA DE COLUMNAS ---
            # Unificamos el nombre de la columna ABC para que coincida con Overstock
            if 'Indicador A B C' in df.columns:
                df = df.rename(columns={'Indicador A B C': 'Indicador ABC'})
            
            for col in ['Vencimiento en meses', 'Meses de stock', 'STOCK ATP', 'Consumo mensual']:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(float)

            if 'Indicador ABC' in df.columns:
                df['Indicador ABC'] = df['Indicador ABC'].astype(str).replace('nan', 'S/D').str.strip()

            # --- 3. PROCESAR UE Y CÓDIGO ---
            def procesar_ue(txt):
                txt = str(txt).strip()
                partes = re.split(r'\s{2,}', txt)
                raiz = partes[0].replace(" ", "") if len(partes) > 1 else txt.replace(" ", "")
                ue = partes[-1] if len(partes) > 1 else "1"
                return pd.Series([raiz, ue])

            # Aseguramos que la columna Material exista
            if 'Material' in df.columns:
                df[['Cod_Limpio', 'UE']] = df['Material'].apply(procesar_ue)
            else:
                st.error("No se encontró la columna 'Material'")
                return

            # --- 4. SEMÁFORO ---
            def semaforo(row):
                acc = str(row.get('Meses de acción', '')).lower()
                if 'vto' in acc or (row.get('Meses de stock', 0) >= row.get('Vencimiento en meses', 99) and row.get('Meses de stock', 0) > 0):
                    return "🔴 CRÍTICO"
                return "🟡 ALERTA" if 'ok' not in acc and row.get('Meses de stock', 0) > 0 else "🟢 ESTABLE"

            df['Estado_Cerebro'] = df.apply(semaforo, axis=1)

            # --- 5. FILTROS ---
            st.subheader("🔍 Filtros de Visualización")
            c1, c2, c3 = st.columns(3)
            with c1:
                niv = st.multiselect("Riesgo:", ["🔴 CRÍTICO", "🟡 ALERTA", "🟢 ESTABLE"], default=["🔴 CRÍTICO", "🟡 ALERTA"])
            with c2:
                busq = st.text_input("Buscar por nombre o código:").strip().replace(" ", "")
            with c3:
                abc_ops = sorted([str(x) for x in df['Indicador ABC'].unique() if str(x) != 'nan'])
                abc_sel = st.multiselect("Categoría:", options=abc_ops, default=abc_ops)

            # --- 6. APLICAR FILTROS ---
            mask = df['Estado_Cerebro'].isin(niv) & df['Indicador ABC'].isin(abc_sel)
            if busq:
                # Buscamos en descripción o código limpio
                desc_col = 'Descripción' if 'Descripción' in df.columns else 'Descripción del material'
                mask = mask & (df['Cod_Limpio'].str.contains(busq, case=False) | df[desc_col].str.contains(busq, case=False))
            
            df_final = df[mask].copy()

            # --- 7. GUARDAR EN MEMORIA (Para la Matriz de Decisiones) ---
            # Esta es la parte que estaba mal ubicada. Ahora se guarda solo el resultado filtrado.
            st.session_state['data_vencimientos'] = df_final

            # --- 8. MOSTRAR TABLA ---
            if not df_final.empty:
                desc_col = 'Descripción' if 'Descripción' in df.columns else 'Descripción del material'
                cols_mostrar = ['Estado_Cerebro', 'Cod_Limpio', desc_col, 'UE', 'Lote', 'STOCK ATP', 'Vencimiento', 'Indicador ABC']
                # Filtrar solo las columnas que existen para evitar errores
                cols_finales = [c for c in cols_mostrar if c in df_final.columns]
                
                df_mostrar = df_final.sort_values(by=['Estado_Cerebro', 'Vencimiento'])
                st.dataframe(df_mostrar[cols_finales], use_container_width=True, hide_index=True)

                # --- 9. SECCIÓN DE DESCARGA ---
                st.write("---")
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df_final.to_excel(writer, index=False, sheet_name='Liquidacion')
                
                st.download_button(
                    label="📥 DESCARGAR SELECCIÓN A EXCEL",
                    data=output.getvalue(),
                    file_name="Planilla_Liquidacion_Wurth.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            else:
                st.warning("No hay productos que coincidan con los filtros seleccionados.")

        except Exception as e:
            st.error(f"Error en procesamiento: {e}")
    else:
        st.info("Carga el archivo para activar el diagnóstico y la comunicación con la Matriz.")
