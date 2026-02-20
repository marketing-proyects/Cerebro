import streamlit as st
import pandas as pd
import re
import io

def mostrar_modulo_liquidation():
    st.header("📦 Módulo de Liquidación Estratégica")
    st.info("Diagnóstico de Inventario por Lote y Unidad de Empaque (UE). Este módulo no utiliza IA.")

    # 1. CUADRO DE NOMENCLATURA
    with st.expander("ℹ️ VER LEYENDA DE CATEGORÍAS (ABC/DEGN)"):
        st.markdown("""
        | Cat | Descripción | Estrategia de Promoción Sugerida |
        | :--- | :--- | :--- |
        | **A** | **Alta Rotación:** Productos estrella. | Ofertas de volumen (ej. 10+1) para asegurar stock en cliente. |
        | **B** | **Media Rotación:** Soporte del catálogo. | Descuentos moderados o combos con productos A. |
        | **C** | **Baja Rotación:** Productos de nicho. | Ofertas para incentivar el despliegue en nuevos clientes. |
        | **D** | **Residual:** Muy baja rotación. | Liquidación agresiva para liberar espacio en depósito. |
        | **E** | **Exhibidores:** Material de apoyo / Display. | Acción inmediata: Colocación en PdV o regalo por compra. |
        | **G** | **Gifts / Regalos:** Material promocional. | No vender. Usar como 'gancho' en promociones de otros items. |
        | **N** | **Nuevos:** Lanzamientos recientes. | Monitoreo. No liquidar a menos que el lanzamiento falle. |
        """)

    archivo = st.file_uploader("Cargar volcado de Vencimientos", type=['xlsx', 'csv'], key="liq_uploader_v_final")

    if archivo:
        try:
            # Lectura
            if archivo.name.endswith('.csv'):
                df = pd.read_csv(archivo)
            else:
                df = pd.read_excel(archivo)
            
            df.columns = df.columns.str.strip()

            # --- LIMPIEZA DE DATOS ---
            cols_num = ['Vencimiento en meses', 'Meses de stock', 'STOCK ATP', 'Consumo mensual']
            for col in cols_num:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(float)

            if 'Indicador A B C' in df.columns:
                df['Indicador A B C'] = df['Indicador A B C'].astype(str).replace('nan', 'S/D').str.strip()
            else:
                df['Indicador A B C'] = 'S/D'

            # --- TRATAMIENTO DE CÓDIGO Y UE ---
            def procesar_codigo_ue(txt):
                txt = str(txt).strip()
                partes = re.split(r'\s{2,}', txt)
                if len(partes) > 1:
                    raiz = partes[0].replace(" ", "")
                    ue = partes[-1]
                else:
                    raiz = txt.replace(" ", "")
                    ue = "1"
                return pd.Series([raiz, ue])

            df[['Cod_Limpio', 'UE']] = df['Material'].apply(procesar_codigo_ue)

            # --- LÓGICA DE SEMÁFORO ---
            def definir_estado(row):
                accion_txt = str(row.get('Meses de acción', '')).strip().lower()
                vto_val = float(row['Vencimiento en meses'])
                stk_val = float(row['Meses de stock'])
                
                if 'vto' in accion_txt or (stk_val > 0 and stk_val >= vto_val):
                    return "🔴 CRÍTICO"
                elif 'ok' not in accion_txt and stk_val > 0:
                    return "🟡 ALERTA"
                else:
                    return "🟢 ESTABLE"

            df['Estado_Cerebro'] = df.apply(definir_estado, axis=1)

            # --- FILTROS ---
            st.subheader("🔍 Filtros de Inventario")
            f1, f2, f3 = st.columns(3)
            with f1:
                niveles = st.multiselect("Estado de Riesgo:", options=["🔴 CRÍTICO", "🟡 ALERTA", "🟢 ESTABLE"], default=["🔴 CRÍTICO", "🟡 ALERTA"])
            with f2:
                busqueda = st.text_input("Buscar (Código, Nombre o Lote):").strip().replace(" ", "")
            with f3:
                abc_ops = sorted([str(x) for x in df['Indicador A B C'].unique() if str(x) != 'nan'])
                abc_sel = st.multiselect("Categoría ABC/DEGN:", options=abc_ops, default=abc_ops)

            # Aplicar filtros
            mask = df['Estado_Cerebro'].isin(niveles) & df['Indicador A B C'].isin(abc_sel)
            if busqueda:
                mask = mask & (df['Cod_Limpio'].str.contains(busqueda, case=False) | 
                               df['Descripción'].str.contains(busqueda, case=False) |
                               df['Lote'].astype(str).str.contains(busqueda))
            
            df_final = df[mask].copy()

            # --- TABLA DE ACCIÓN ---
            st.subheader("📋 Detalle de Criticidad y Empaque (UE)")
            cols_ver = ['Estado_Cerebro', 'Cod_Limpio', 'Descripción', 'UE', 'Lote', 'STOCK ATP', 'Vencimiento', 'Vencimiento en meses', 'Meses de stock', 'Indicador A B C']
            
            df_final = df_final.sort_values(by=['Estado_Cerebro', 'Vencimiento en meses'], ascending=[True, True])

            st.dataframe(df_final[cols_ver], use_container_width=True, hide_index=True)

            # --- BOTÓN DE DESCARGA EXCEL ---
            if not df_final.empty:
                # Preparamos el archivo Excel en memoria
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df_final[cols_ver].to_excel(writer, index=False, sheet_name='Liquidacion_Filtrada')
                
                processed_data = output.getvalue()
                
                st.download_button(
                    label="📥 Descargar este listado en Excel",
                    data=processed_data,
                    file_name="Reporte_Liquidacion_Wurth.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            else:
                st.warning("No hay datos filtrados para descargar.")

        except Exception as e:
            st.error(f"Error al procesar el archivo: {e}")
    else:
        st.info("Carga el reporte de vencimientos para analizar los lotes y las UE.")
