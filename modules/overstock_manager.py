import streamlit as st
import pandas as pd
import re
import io
import plotly.express as px

def mostrar_modulo_overstock():
    st.header("📊 Análisis de Overstock") 
    st.info("Diagnóstico de capital inmovilizado basado en la Curva de Rotación UY.")

    NOMENCLATURA = {
        'A': 'A - Consumibles (Alta Rotación)',
        'B': 'B - Insumos (Rotación Constante)',
        'C': 'C - Mantenimiento (Rotación Media)',
        'D': 'D - Equipos (Rotación Baja)',
        'E': 'E - Herramientas Técnicas (Baja Rotación / Alto Valor)',
        'F': 'F - Artículos de Nicho (Rotación Crítica)',
        'G': 'G - Inactivos / Outlet (Sin Venta Reciente)',
        'N': 'N - Nuevos / Lanzamientos',
        'S/D': 'S/D - Sin Datos'
    }

    # --- AYUDA: Categorías y Semáforo ---
    c_h1, c_h2 = st.columns(2)
    with c_h1:
        with st.expander("ℹ️ LEYENDA DE ROTACIÓN"):
            st.markdown("""
            | Cat | Tipo de Producto |
            | :--- | :--- |
            | **A / B** | Alta Rotación. |
            | **C / D** | Rotación Media. |
            | **E / F** | Rotación Baja (Caro). |
            | **G** | Inactivos / Outlet. |
            """)
    with c_h2:
        with st.expander("🚦 SEMÁFORO DE SALUD"):
            st.markdown("""
            | Estado | Condición |
            | :--- | :--- |
            | 🔴 **RIESGO** | > 12 meses stock |
            | ⚪ **PARADO** | Stock > 0, Venta 0 |
            | 🟡 **ALERTA** | 6-12 meses stock |
            """)

    archivo = st.file_uploader("Cargar reporte de Sobre-stock", type=['xlsx', 'csv'], key="overstock_forense")

    if archivo:
        try:
            df = pd.read_csv(archivo) if archivo.name.endswith('.csv') else pd.read_excel(archivo)
            df.columns = df.columns.str.strip()

            # Limpieza
            for col in ['ATP-quantity', 'Meses de stock ATP', 'Importe disponible para acciones', 'Promedio de venta mensual']:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(float)

            df['Indicador ABC'] = df['Indicador ABC'].astype(str).replace('nan', 'S/D').str.strip()

            def procesar_ue(txt):
                txt = str(txt).strip()
                partes = re.split(r'\s{2,}', txt)
                raiz = partes[0].replace(" ", "") if len(partes) > 1 else txt.replace(" ", "")
                ue = partes[-1] if len(partes) > 1 else "1"
                return pd.Series([raiz, ue])
            
            df[['Cod_Limpio', 'UE']] = df['Material'].apply(procesar_ue)

            def definir_salud(row):
                if row['ATP-quantity'] > 0 and row['Promedio de venta mensual'] == 0:
                    return "⚪ SIN MOVIMIENTO"
                return "🔴 RIESGO CONTABLE" if row['Meses de stock ATP'] > 12 else ("🟡 EXCEDENTE" if row['Meses de stock ATP'] >= 6 else "🟢 SALUDABLE")
            
            df['Salud_Inventario'] = df.apply(definir_salud, axis=1)

            # Filtros
            st.subheader("🔍 Filtros de Impacto")
            c1, c2, c3 = st.columns(3)
            with c1:
                salud_sel = st.multiselect("Riesgo:", ["🔴 RIESGO CONTABLE", "⚪ SIN MOVIMIENTO", "🟡 EXCEDENTE", "🟢 SALUDABLE"], default=["🔴 RIESGO CONTABLE", "⚪ SIN MOVIMIENTO"])
            with c2:
                busqueda = st.text_input("Buscar Producto:").strip()
            with c3:
                abc_ops = sorted([str(x) for x in df['Indicador ABC'].unique() if str(x) != 'nan'])
                abc_sel = st.multiselect("Categoría:", options=abc_ops, default=abc_ops)

            mask = df['Salud_Inventario'].isin(salud_sel) & df['Indicador ABC'].isin(abc_sel)
            if busqueda:
                mask = mask & (df['Cod_Limpio'].str.contains(busqueda, case=False) | df['Descripción del material'].str.contains(busqueda, case=False))
            
            df_final = df[mask].copy()

            # --- GUARDADO PARA LA MATRIZ ---
            st.session_state['data_overstock'] = df_final

            # Métricas y Gráfico
            st.markdown("---")
            m1, m2, m3 = st.columns(3)
            m1.metric("Lotes Críticos", len(df_final))
            cap_inv = df_final['Importe disponible para acciones'].sum()
            m2.metric("Capital Inmovilizado", f"$ {cap_inv:,.0f}")
            m3.metric("Potencial Recuperación (50%)", f"$ {(cap_inv * 0.5):,.0f}")

            if not df_final.empty:
                df_grafico = df_final.groupby('Indicador ABC')['Importe disponible para acciones'].sum().reset_index()
                df_grafico['Nivel'] = df_grafico['Indicador ABC'].map(NOMENCLATURA).fillna(df_grafico['Indicador ABC'])
                fig = px.pie(df_grafico, values='Importe disponible para acciones', names='Nivel', hole=0.4, color_discrete_sequence=px.colors.sequential.Reds_r)
                st.plotly_chart(fig, use_container_width=True)

            # Tabla y Descarga
            cols_ver = ['Salud_Inventario', 'Cod_Limpio', 'Descripción del material', 'UE', 'ATP-quantity', 'Meses de stock ATP', 'Importe disponible para acciones', 'Indicador ABC']
            st.dataframe(df_final[cols_ver], use_container_width=True, hide_index=True)

            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df_final[cols_ver].to_excel(writer, index=False, sheet_name='Overstock')
            st.download_button(label="📥 Exportar Excel", data=output.getvalue(), file_name="Overstock_Analizado.xlsx", use_container_width=True)

        except Exception as e:
            st.error(f"Error: {e}")
