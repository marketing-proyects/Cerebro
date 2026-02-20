import streamlit as st
import pandas as pd
import re
import io
import plotly.express as px

def mostrar_modulo_overstock():
    st.header("📊 Gestión de Sobre-stock y Recuperación de Capital")
    st.info("Diagnóstico de capital inmovilizado basado en la Curva de Rotación de Uruguay.")

    # DICCIONARIO DE NOMENCLATURA REAL (Basado en el análisis de productos)
    NOMENCLATURA = {
        'A': 'A - Consumibles / Alta Rotación',
        'B': 'B - Herramientas e Insumos / Rotación Alta',
        'C': 'C - Maquinaria y Químicos / Rotación Media',
        'D': 'D - Maquinaria Pesada / Rotación Baja',
        'E': 'E - Herramientas Específicas / Rotación Muy Baja',
        'F': 'F - Artículos Técnicos / Rotación Crítica',
        'G': 'G - Accesorios y Especialidades / Rotación Errática',
        'N': 'N - Lanzamientos / Nuevos',
        'S/D': 'S/D - Sin Clasificación'
    }

    # --- AYUDA 1: Categorías Reales ---
    with st.expander("ℹ️ 1. LEYENDA TÉCNICA (Basada en Productos Reales)"):
        st.markdown("""
        | Cat | Tipo de Producto Típico | Comportamiento Financiero |
        | :--- | :--- | :--- |
        | **A / B** | Limpiadores, Papel, Zapatos, Herramientas manuales. | **Flujo de Caja:** Dinero en movimiento constante. |
        | **C / D** | Hidrolavadoras, Amoladoras, Aceites 200L. | **Inmovilizado Medio:** Ocupan volumen y capital moderado. |
        | **E / F / G**| Dinamométricas, Jump Starters, Carros, Spoter. | **Alto Riesgo:** Productos caros de venta lenta. |
        | **N** | Lanzamientos recientes. | **Incertidumbre:** Pendiente de confirmar rotación real. |
        """)

    # --- AYUDA 2: Semáforo ---
    with st.expander("🚦 2. LÓGICA DEL SEMÁFORO"):
        st.markdown("""
        | Estado | Condición | Riesgo Contable |
        | :--- | :--- | :--- |
        | 🔴 **RIESGO CONTABLE** | > 12 meses de stock | Requiere provisión por obsolescencia. |
        | ⚪ **SIN MOVIMIENTO** | Stock > 0 y Venta = 0 | Capital "muerto". Acción inmediata necesaria. |
        | 🟡 **EXCEDENTE** | 6 a 12 meses de stock | Alerta de sobre-compra. |
        | 🟢 **SALUDABLE** | < 6 meses de stock | Rotación óptima. |
        """)

    archivo = st.file_uploader("Cargar reporte de Sobre-stock", type=['xlsx', 'csv'], key="overstock_uy_v1")

    if archivo:
        try:
            df = pd.read_csv(archivo) if archivo.name.endswith('.csv') else pd.read_excel(archivo)
            df.columns = df.columns.str.strip()

            # --- LIMPIEZA ---
            for col in ['ATP-quantity', 'Meses de stock ATP', 'Importe disponible para acciones', 'Promedio de venta mensual']:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(float)

            df['Indicador ABC'] = df['Indicador ABC'].astype(str).replace('nan', 'S/D').str.strip() if 'Indicador ABC' in df.columns else 'S/D'

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

            # --- FILTROS ---
            st.subheader("🔍 Filtros de Impacto")
            c1, c2, c3 = st.columns(3)
            with c1:
                salud_sel = st.multiselect("Riesgo:", ["🔴 RIESGO CONTABLE", "⚪ SIN MOVIMIENTO", "🟡 EXCEDENTE", "🟢 SALUDABLE"], default=["🔴 RIESGO CONTABLE", "⚪ SIN MOVIMIENTO"])
            with c2:
                busqueda = st.text_input("Buscar Producto:").strip().replace(" ", "")
            with c3:
                abc_ops = sorted([str(x) for x in df['Indicador ABC'].unique() if str(x) != 'nan'])
                abc_sel = st.multiselect("Rotación:", options=abc_ops, default=abc_ops)

            mask = df['Salud_Inventario'].isin(salud_sel) & df['Indicador ABC'].isin(abc_sel)
            if busqueda:
                mask = mask & (df['Cod_Limpio'].str.contains(busqueda, case=False) | df['Descripción del material'].str.contains(busqueda, case=False))
            df_final = df[mask].copy()

            # --- MÉTRICAS ---
            st.markdown("---")
            m1, m2, m3 = st.columns(3)
            m1.metric("Lotes Críticos", len(df_final))
            cap_inv = df_final['Importe disponible para acciones'].sum()
            m2.metric("Capital Inmovilizado", f"$ {cap_inv:,.0f}")
            m3.metric("Recuperación (50%)", f"$ {(cap_inv * 0.5):,.0f}")

            # --- GRÁFICO DE TORTA AUTO-EXPLICATIVO ---
            if not df_final.empty:
                st.subheader("📊 Capital Atrapado por Nivel de Rotación")
                df_grafico = df_final.groupby('Indicador ABC')['Importe disponible para acciones'].sum().reset_index()
                df_grafico['Categoría'] = df_grafico['Indicador ABC'].map(NOMENCLATURA).fillna(df_grafico['Indicador ABC'])
                
                fig = px.pie(df_grafico, values='Importe disponible para acciones', names='Categoría', hole=0.4,
                             color_discrete_sequence=px.colors.sequential.Reds_r)
                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True)

            # --- TABLA Y DESCARGA ---
            st.subheader("📋 Detalle de Artículos Estancados")
            cols_ver = ['Salud_Inventario', 'Cod_Limpio', 'Descripción del material', 'UE', 'ATP-quantity', 'Meses de stock ATP', 'Importe disponible para acciones', 'Indicador ABC']
            df_final = df_final.sort_values(by='Importe disponible para acciones', ascending=False)
            st.dataframe(df_final[cols_ver], use_container_width=True, hide_index=True)

            if not df_final.empty:
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df_final[cols_ver].to_excel(writer, index=False, sheet_name='Overstock')
                st.download_button(label="📥 Exportar Excel de Acciones", data=output.getvalue(), file_name="Planilla_Overstock_Wurth.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)

        except Exception as e:
            st.error(f"Error: {e}")
