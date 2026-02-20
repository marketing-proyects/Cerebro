import streamlit as st
import pandas as pd
import re
import io

def mostrar_modulo_overstock():
    st.header("📊 Gestión de Sobre-stock y Recuperación de Capital")
    st.info("Análisis de inercia de venta para identificar capital inmovilizado.")

    # 1. Glosario Técnico de Sobre-stock
    with st.expander("ℹ️ LÓGICA DE DIAGNÓSTICO (Inercia de Venta)"):
        st.markdown("""
        | Estado | Condición (Meses de Stock) | Acción Sugerida |
        | :--- | :--- | :--- |
        | 🔴 **CRÍTICO** | > 12 meses | Liquidación agresiva. |
        | 🟡 **EXCEDENTE** | 6 a 12 meses | Frenar compras y activar promociones de volumen. |
        | 🟢 **SALUDABLE** | < 6 meses | Flujo normal. Reposición estándar. |
        | ⚪ **INACTIVO** | Venta = 0 con Stock | Riesgo total. Evaluar obsolescencia o campaña especial. |
        """)

    archivo = st.file_uploader("Cargar reporte de Sobre-stock (Overstock)", type=['xlsx', 'csv'], key="overstock_uploader")

    if archivo:
        try:
            df = pd.read_csv(archivo) if archivo.name.endswith('.csv') else pd.read_excel(archivo)
            df.columns = df.columns.str.strip()

            # --- LIMPIEZA DE DATOS ---
            cols_num = ['ATP-quantity', 'Meses de stock ATP', 'Importe disponible para acciones', 'Promedio de venta mensual']
            for col in cols_num:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(float)

            # --- TRATAMIENTO DE CÓDIGO Y UE ---
            def procesar_ue(txt):
                txt = str(txt).strip()
                partes = re.split(r'\s{2,}', txt)
                raiz = partes[0].replace(" ", "") if len(partes) > 1 else txt.replace(" ", "")
                ue = partes[-1] if len(partes) > 1 else "1"
                return pd.Series([raiz, ue])

            df[['Cod_Limpio', 'UE']] = df['Material'].apply(procesar_ue)

            # --- LÓGICA DE SEMÁFORO DE SALUD ---
            def definir_salud(row):
                meses = row['Meses de stock ATP']
                venta = row['Promedio de venta mensual']
                stock = row['ATP-quantity']
                
                if stock > 0 and venta == 0:
                    return "⚪ INACTIVO"
                elif meses > 12:
                    return "🔴 CRÍTICO"
                elif meses >= 6:
                    return "🟡 EXCEDENTE"
                else:
                    return "🟢 SALUDABLE"

            df['Salud_Inventario'] = df.apply(definir_salud, axis=1)

            # --- FILTROS ---
            st.subheader("🔍 Filtros de Análisis")
            c1, c2, c3 = st.columns(3)
            with c1:
                salud_sel = st.multiselect("Salud de Stock:", ["🔴 CRÍTICO", "🟡 EXCEDENTE", "⚪ INACTIVO", "🟢 SALUDABLE"], default=["🔴 CRÍTICO", "⚪ INACTIVO"])
            with c2:
                busqueda = st.text_input("Buscar Producto/Código:").strip().replace(" ", "")
            with c3:
                abc_ops = sorted([str(x) for x in df['Indicador ABC'].unique()]) if 'Indicador ABC' in df.columns else []
                abc_sel = st.multiselect("Categoría ABC/DEGN:", options=abc_ops, default=abc_ops)

            # Aplicar Filtros
            mask = df['Salud_Inventario'].isin(salud_sel)
            if abc_sel:
                mask = mask & df['Indicador ABC'].isin(abc_sel)
            if busqueda:
                mask = mask & (df['Cod_Limpio'].str.contains(busqueda, case=False) | df['Descripción del material'].str.contains(busqueda, case=False))
            
            df_final = df[mask].copy()

            # --- MÉTRICAS DE IMPACTO ---
            st.markdown("---")
            m1, m2, m3 = st.columns(3)
            m1.metric("Items en Riesgo", len(df_final))
            m2.metric("Total Stock ATP", f"{int(df_final['ATP-quantity'].sum()):,}")
            # El importe nos da el valor real del capital inmovilizado
            importe_total = df_final['Importe disponible para acciones'].sum()
            m3.metric("Capital Inmovilizado", f"$ {importe_total:,.2f}")

            # --- TABLA DE RESULTADOS ---
            st.subheader("📋 Listado de Recuperación de Capital")
            cols_ver = [
                'Salud_Inventario', 'Cod_Limpio', 'Descripción del material', 'UE', 
                'ATP-quantity', 'Meses de stock ATP', 'Promedio de venta mensual', 
                'Importe disponible para acciones', 'Indicador ABC'
            ]
            
            df_final = df_final.sort_values(by=['Importe disponible para acciones', 'Meses de stock ATP'], ascending=False)
            
            st.dataframe(df_final[cols_ver], use_container_width=True, hide_index=True)

            # --- BOTÓN DE DESCARGA ---
            if not df_final.empty:
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df_final[cols_ver].to_excel(writer, index=False, sheet_name='Overstock')
                
                st.download_button(
                    label="📥 Descargar Planilla de Acciones Comerciales",
                    data=output.getvalue(),
                    file_name="Planilla_Overstock_Wurth.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )

        except Exception as e:
            st.error(f"Error al analizar el sobre-stock: {e}")
    else:
        st.info("Suba el reporte de stock para identificar el capital inmovilizado.")
