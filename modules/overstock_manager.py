import streamlit as st
import pandas as pd
import re
import io
import plotly.express as px

def mostrar_modulo_overstock():
    st.header("📊 Gestión de Overstock / Recuperación de Capital")
    st.info("Análisis capital inmovilizado basado en la Curva de Rotación UY.")

    # NOMENCLATURA REAL DEDUCIDA
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

    # --- AYUDA 1: Categorías ---
    with st.expander("ℹ️ 1. LEYENDA TÉCNICA (Niveles de Rotación UY)"):
        st.markdown("""
        | Cat | Comportamiento del Capital | Acción Sugerida |
        | :--- | :--- | :--- |
        | **A / B** | **Liquidez Inmediata:** Alta rotación. | No liquidar. Asegurar reposición. |
        | **C / D** | **Inversión Moderada:** Maquinaria y Químicos. | Ofertas de volumen para evitar excedentes. |
        | **E / F** | **Capital Pesado:** Herramientas de alto valor. | **Acción Comercial:** Venta técnica dirigida. |
        | **G** | **Costo Hundido:** Sin ventas o en Outlet. | **Liquidación:** Recuperar cualquier % de capital. |
        | **N** | **Fase Inicial:** Productos nuevos. | Monitorear adopción del mercado. |
        """)

    # --- AYUDA 2: Semáforo ---
    with st.expander("🚦 2. SEMÁFORO DE SALUD DE INVENTARIO"):
        st.markdown("""
        | Estado | Condición | Impacto en Balance |
        | :--- | :--- | :--- |
        | 🔴 **RIESGO CONTABLE** | > 12 meses de stock | Requiere provisión por obsolescencia. |
        | ⚪ **SIN MOVIMIENTO** | Stock > 0 y Venta = 0 | Capital estancado. Máxima prioridad. |
        | 🟡 **EXCEDENTE** | 6 a 12 meses de stock | Inversión por encima del flujo ideal. |
        | 🟢 **SALUDABLE** | < 6 meses de stock | Ciclo de venta y reposición sano. |
        """)

    archivo = st.file_uploader("Cargar reporte de Sobre-stock", type=['xlsx', 'csv'], key="overstock_forense")

    if archivo:
        try:
            df = pd.read_csv(archivo) if archivo.name.endswith('.csv') else pd.read_excel(archivo)
            df.columns = df.columns.str.strip()

            # Limpieza de numéricos
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

            # Métricas
            st.markdown("---")
            m1, m2, m3 = st.columns(3)
            m1.metric("Lotes Críticos", len(df_final))
            cap_inv = df_final['Importe disponible para acciones'].sum()
            m2.metric("Capital Inmovilizado", f"$ {cap_inv:,.0f}")
            m3.metric("Potencial Recuperación", f"$ {(cap_inv * 0.5):,.0f}")

            # Gráfico de Torta Forense
            if not df_final.empty:
                st.subheader("📊 Distribución del Capital Atrapado")
                df_grafico = df_final.groupby('Indicador ABC')['Importe disponible para acciones'].sum().reset_index()
                df_grafico['Nivel'] = df_grafico['Indicador ABC'].map(NOMENCLATURA).fillna(df_grafico['Indicador ABC'])
                
                fig = px.pie(df_grafico, values='Importe disponible para acciones', names='Nivel', hole=0.4,
                             color_discrete_sequence=px.colors.sequential.Reds_r)
                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True)

            # Tabla
            st.subheader("📋 Artículos Analizados")
            cols_ver = ['Salud_Inventario', 'Cod_Limpio', 'Descripción del material', 'UE', 'ATP-quantity', 'Meses de stock ATP', 'Importe disponible para acciones', 'Indicador ABC']
            df_final = df_final.sort_values(by='Importe disponible para acciones', ascending=False)
            st.dataframe(df_final[cols_ver], use_container_width=True, hide_index=True)

            if not df_final.empty:
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df_final[cols_ver].to_excel(writer, index=False, sheet_name='Overstock')
                st.download_button(label="📥 Exportar Excel", data=output.getvalue(), file_name="Overstock_Acciones_UY.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)

        except Exception as e:
            st.error(f"Error: {e}")
