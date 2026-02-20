import streamlit as st
import pandas as pd
import re
import io

def mostrar_modulo_liquidation():
    st.header("📦 Módulo de Liquidación Estratégica")
    st.info("Diagnóstico de Inventario por Lote y Unidad de Empaque (UE).")

    # 1. Glosario
    with st.expander("ℹ️ VER LEYENDA DE CATEGORÍAS (ABC/DEGN)"):
        st.markdown("""
        | Cat | Descripción | Estrategia ante Vencimiento |
        | :--- | :--- | :--- |
        | **A** | **Alta Rotación:** Artículos estrella. | Ofertas de volumen (10+1) para stockear al cliente. |
        | **B** | **Media Rotación:** Soporte de venta. | Combos con productos A para mover el lote viejo. |
        | **C** | **Baja Rotación:** Productos de nicho. | Incentivar la primera compra con descuento agresivo. |
        | **D** | **Residual:** Rotación mínima. | **Liquidación Total:** El objetivo es que salga antes de vencer. |
        | **E** | **Exhibidores:** Material de display. | Colocación inmediata en punto de venta (PdV). |
        | **G** | **Gifts / Regalos:** Promocionales. | Regalar por la compra de productos con riesgo 🔴. |
        | **N** | **Nuevos:** Lanzamientos. | Revisar por qué no rotó en el lanzamiento. |
        | **S/D**| **Sin Datos:** No clasificado. | Revisar estado del artículo en el maestro. |
        """)

    archivo = st.file_uploader("Cargar volcado de Vencimientos", type=['xlsx', 'csv'], key="liq_uploader_v_final")

    if archivo:
        df_final = pd.DataFrame() # Inicializamos vacío
        
        try:
            # Lectura
            df = pd.read_csv(archivo) if archivo.name.endswith('.csv') else pd.read_excel(archivo)
            df.columns = df.columns.str.strip()

            # Limpieza de números
            for col in ['Vencimiento en meses', 'Meses de stock', 'STOCK ATP', 'Consumo mensual']:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(float)

            # Limpieza ABC
            if 'Indicador A B C' in df.columns:
                df['Indicador A B C'] = df['Indicador A B C'].astype(str).replace('nan', 'S/D').str.strip()

            # Procesar UE y Código
            def procesar_ue(txt):
                txt = str(txt).strip()
                partes = re.split(r'\s{2,}', txt)
                raiz = partes[0].replace(" ", "") if len(partes) > 1 else txt.replace(" ", "")
                ue = partes[-1] if len(partes) > 1 else "1"
                return pd.Series([raiz, ue])

            df[['Cod_Limpio', 'UE']] = df['Material'].apply(procesar_ue)

            # Semáforo
            def semaforo(row):
                acc = str(row.get('Meses de acción', '')).lower()
                if 'vto' in acc or (row['Meses de stock'] > 0 and row['Meses de stock'] >= row['Vencimiento en meses']):
                    return "🔴 CRÍTICO"
                return "🟡 ALERTA" if 'ok' not in acc and row['Meses de stock'] > 0 else "🟢 ESTABLE"

            df['Estado_Cerebro'] = df.apply(semaforo, axis=1)

            # Filtros
            st.subheader("🔍 Filtros")
            c1, c2, c3 = st.columns(3)
            with c1:
                niv = st.multiselect("Riesgo:", ["🔴 CRÍTICO", "🟡 ALERTA", "🟢 ESTABLE"], default=["🔴 CRÍTICO", "🟡 ALERTA"])
            with c2:
                busq = st.text_input("Buscar:").strip().replace(" ", "")
            with c3:
                abc_ops = sorted([str(x) for x in df['Indicador A B C'].unique() if str(x) != 'nan'])
                abc_sel = st.multiselect("Categoría:", options=abc_ops, default=abc_ops)

            # Aplicar Filtro
            mask = df['Estado_Cerebro'].isin(niv) & df['Indicador A B C'].isin(abc_sel)
            if busq:
                mask = mask & (df['Cod_Limpio'].str.contains(busq, case=False) | df['Descripción'].str.contains(busq, case=False))
            
            df_final = df[mask].copy()

            # Mostrar Tabla
            if not df_final.empty:
                cols = ['Estado_Cerebro', 'Cod_Limpio', 'Descripción', 'UE', 'Lote', 'STOCK ATP', 'Vencimiento', 'Indicador A B C']
                df_final = df_final.sort_values(by=['Estado_Cerebro', 'Vencimiento'])
                st.dataframe(df_final[cols], use_container_width=True, hide_index=True)
            else:
                st.warning("No hay productos que coincidan con los filtros seleccionados.")

        except Exception as e:
            st.error(f"Error en procesamiento: {e}")

        # --- SECCIÓN DE DESCARGA (Fuera del try de procesamiento para mayor visibilidad) ---
        if not df_final.empty:
            st.write("---")
            try:
                output = io.BytesIO()
                # Intentamos usar xlsxwriter
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df_final.to_excel(writer, index=False, sheet_name='Liquidacion')
                
                st.download_button(
                    label="📥 DESCARGAR SELECCIÓN A EXCEL",
                    data=output.getvalue(),
                    file_name="Planilla_Liquidacion_Wurth.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            except ModuleNotFoundError:
                st.error("Error: Falta la librería 'xlsxwriter'. Agrégala a tu requirements.txt")
            except Exception as e:
                st.error(f"Error al generar Excel: {e}")

    else:
        st.info("Carga el archivo para activar el diagnóstico y la descarga.")
