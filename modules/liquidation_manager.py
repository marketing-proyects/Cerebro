import streamlit as st
import pandas as pd
import re
import io

def mostrar_modulo_liquidation():
    st.header("📦 Análisis de Vencimientos")
    st.info("Diagnóstico de lotes con riesgo de caducidad y salud de inventario.")

    # 1. LEYENDA TÉCNICA
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

    archivo = st.file_uploader("Cargar volcado de Vencimientos", type=['xlsx', 'csv'], key="liq_v_final")

    if archivo:
        try:
            # Lectura
            df = pd.read_csv(archivo) if archivo.name.endswith('.csv') else pd.read_excel(archivo)
            df.columns = df.columns.str.strip()

            # --- LIMPIEZA Y UNIFICACIÓN ---
            if 'Indicador A B C' in df.columns:
                df = df.rename(columns={'Indicador A B C': 'Indicador ABC'})
            
            cols_num = ['Vencimiento en meses', 'Meses de stock', 'STOCK ATP', 'Consumo mensual']
            for col in cols_num:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(float)

            if 'Indicador ABC' in df.columns:
                df['Indicador ABC'] = df['Indicador ABC'].astype(str).replace('nan', 'S/D').str.strip()

            # Procesar UE y Código
            def procesar_ue(txt):
                txt = str(txt).strip()
                partes = re.split(r'\s{2,}', txt)
                raiz = partes[0].replace(" ", "") if len(partes) > 1 else txt.replace(" ", "")
                ue = partes[-1] if len(partes) > 1 else "1"
                return pd.Series([raiz, ue])

            if 'Material' in df.columns:
                df[['Cod_Limpio', 'UE']] = df['Material'].apply(procesar_ue)
            else:
                st.error("No se encontró la columna 'Material'")
                return

            # Semáforo
            def semaforo(row):
                vto = row.get('Vencimiento en meses', 99)
                stk = row.get('Meses de stock', 0)
                acc = str(row.get('Meses de acción', '')).lower()
                
                if 'vto' in acc or (stk >= vto and stk > 0):
                    return "🔴 CRÍTICO"
                return "🟡 ALERTA" if 'ok' not in acc and stk > 0 else "🟢 ESTABLE"

            df['Estado_Cerebro'] = df.apply(semaforo, axis=1)

            # Filtros
            st.subheader("🔍 Filtros de Diagnóstico")
            c1, c2, c3 = st.columns(3)
            with c1:
                niv = st.multiselect("Riesgo:", ["🔴 CRÍTICO", "🟡 ALERTA", "🟢 ESTABLE"], default=["🔴 CRÍTICO", "🟡 ALERTA"])
            with c2:
                busq = st.text_input("Buscar nombre o código:").strip().replace(" ", "")
            with c3:
                abc_ops = sorted([str(x) for x in df['Indicador ABC'].unique() if str(x) != 'nan'])
                abc_sel = st.multiselect("Categoría ABC:", options=abc_ops, default=abc_ops)

            # Aplicar Filtros
            desc_col = 'Descripción' if 'Descripción' in df.columns else 'Descripción del material'
            mask = df['Estado_Cerebro'].isin(niv) & df['Indicador ABC'].isin(abc_sel)
            if busq:
                mask = mask & (df['Cod_Limpio'].str.contains(busq, case=False) | df[desc_col].str.contains(busq, case=False))
            
            df_final = df[mask].copy()

            # --- GUARDADO PARA LA MATRIZ ---
            st.session_state['data_vencimientos'] = df_final

            # Mostrar Tabla
            if not df_final.empty:
                st.success(f"✅ {len(df_final)} artículos listos para análisis.")
                cols_mostrar = ['Estado_Cerebro', 'Cod_Limpio', desc_col, 'UE', 'Lote', 'STOCK ATP', 'Vencimiento', 'Indicador ABC']
                cols_finales = [c for c in cols_mostrar if c in df_final.columns]
                
                df_mostrar = df_final.sort_values(by=['Estado_Cerebro', 'Vencimiento'])
                st.dataframe(df_mostrar[cols_finales], use_container_width=True, hide_index=True)

                # Descarga
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df_final.to_excel(writer, index=False, sheet_name='Vencimientos')
                
                st.download_button(label="📥 Exportar Excel", data=output.getvalue(), file_name="Vencimientos_Analizados.xlsx", use_container_width=True)
            else:
                st.warning("No hay productos con los filtros seleccionados.")

        except Exception as e:
            st.error(f"Error: {e}")
