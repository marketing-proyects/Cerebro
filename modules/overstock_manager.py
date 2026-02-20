import streamlit as st
import pandas as pd
import re
import io
import plotly.express as px

def mostrar_modulo_overstock():
    st.header("📊 Gestión de Sobre-stock y Recuperación de Capital")
    
    # Diccionario maestro de nomenclaturas para usar en tablas y gráficos
    NOMENCLATURA = {
        'A': 'A - Alta Rotación',
        'B': 'B - Media Rotación',
        'C': 'C - Baja Rotación',
        'D': 'D - Residual',
        'E': 'E - Exhibidores',
        'F': 'F - Fuera de Catálogo',
        'G': 'G - Gifts / Regalos',
        'N': 'N - Nuevos',
        'S/D': 'S/D - Sin Datos'
    }

    # --- BLOQUE DE AYUDA 1: Categorías ---
    with st.expander("ℹ️ 1. LEYENDA DE CATEGORÍAS (ABC/DEGN)"):
        # Generamos la tabla de la leyenda dinámicamente o fija para control total
        st.markdown("""
        | Cat | Descripción | Estrategia para Recuperar Capital |
        | :--- | :--- | :--- |
        | **A** | **Alta Rotación** | No liquidar. Frenar compras hasta normalizar stock. |
        | **B** | **Media Rotación** | Promover venta cruzada (Cross-selling). |
        | **C** | **Baja Rotación** | Ofertas especiales para liberar espacio. |
        | **D** | **Residual** | **Acción Agresiva:** Recuperar el costo (Cash-out). |
        | **E** | **Exhibidores** | Enviar a clientes estratégicos inmediatamente. |
        | **F** | **Fuera de Catálogo** | Liquidar o dar de baja si no tiene mercado. |
        | **G** | **Gifts / Regalos** | Usar como incentivo para vender productos C/D. |
        | **N** | **Nuevos** | Monitorear aceptación del mercado. |
        """)

    # --- BLOQUE DE AYUDA 2: Semáforo ---
    with st.expander("🚦 2. LÓGICA DEL SEMÁFORO (Meses de Stock)"):
        st.markdown("""
        | Estado | Condición | Riesgo Contable |
        | :--- | :--- | :--- |
        | 🔴 **RIESGO CONTABLE** | > 12 meses de stock | **Muy Alto:** Capital dormido hace más de un año. |
        | ⚪ **SIN ROTACIÓN** | Stock > 0 y Venta = 0 | **Extremo:** Sin inercia. Peligro de pérdida total. |
        | 🟡 **EXCEDENTE** | 6 a 12 meses de stock | **Medio:** Stock por encima de la media de seguridad. |
        | 🟢 **SALUDABLE** | < 6 meses de stock | **Bajo:** Rotación normal. |
        """)

    archivo = st.file_uploader("Cargar reporte de Sobre-stock (Overstock)", type=['xlsx', 'csv'], key="overstock_f_update")

    if archivo:
        try:
            df = pd.read_csv(archivo) if archivo.name.endswith('.csv') else pd.read_excel(archivo)
            df.columns = df.columns.str.strip()

            # --- LIMPIEZA ---
            cols_num = ['ATP-quantity', 'Meses de stock ATP', 'Importe disponible para acciones', 'Promedio de venta mensual']
            for col in cols_num:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(float)

            df['Indicador ABC'] = df['Indicador ABC'].astype(str).replace('nan', 'S/D').str.strip() if 'Indicador ABC' in df.columns else 'S/D'

            # --- TRATAMIENTO CÓDIGO/UE ---
            def procesar_ue(txt):
                txt = str(txt).strip()
                partes = re.split(r'\s{2,}', txt)
                raiz = partes[0].replace(" ", "") if len(partes) > 1 else txt.replace(" ", "")
                ue = partes[-1] if len(partes) > 1 else "1"
                return pd.Series([raiz, ue])
            df[['Cod_Limpio', 'UE']] = df['Material'].apply(procesar_ue)

            # --- SALUD INVENTARIO ---
            def definir_salud(row):
                if row['ATP-quantity'] > 0 and row['Promedio de venta mensual'] == 0:
                    return "⚪ SIN ROTACIÓN"
                return "🔴 RIESGO CONTABLE" if row['Meses de stock ATP'] > 12 else ("🟡 EXCEDENTE" if row['Meses de stock ATP'] >= 6 else "🟢 SALUDABLE")
            df['Salud_Inventario'] = df.apply(definir_salud, axis=1)

            # --- FILTROS ---
            st.subheader("🔍 Filtros de Impacto")
            c1, c2, c3 = st.columns(3)
            with c1:
                salud_sel = st.multiselect("Nivel de Riesgo:", ["🔴 RIESGO CONTABLE", "⚪ SIN ROTACIÓN", "🟡 EXCEDENTE", "🟢 SALUDABLE"], default=["🔴 RIESGO CONTABLE", "⚪ SIN ROTACIÓN"])
            with c2:
                busqueda = st.text_input("Buscar por Código o Nombre:").strip().replace(" ", "")
            with c3:
                abc_ops = sorted([str(x) for x in df['Indicador ABC'].unique() if str(x) != 'nan'])
                abc_sel = st.multiselect("Categoría ABC/DEGN:", options=abc_ops, default=abc_ops)

            # Aplicar Filtros
            mask = df['Salud_Inventario'].isin(salud_sel) & df['Indicador ABC'].isin(abc_sel)
            if busqueda:
                mask = mask & (df['Cod_Limpio'].str.contains(busqueda, case=False) | df['Descripción del material'].str.contains(busqueda, case=False))
            df_final = df[mask].copy()

            # --- MÉTRICAS ---
            st.markdown("---")
            m1, m2, m3 = st.columns(3)
            m1.metric("Lotes en Riesgo", len(df_final))
            cap_inv = df_final['Importe disponible para acciones'].sum()
            m2.metric("Capital Inmovilizado", f"$ {cap_inv:,.0f}")
            m3.metric("Recuperación Potencial (50%)", f"$ {(cap_inv * 0.5):,.0f}")

            # --- GRÁFICO DE TORTA MEJORADO ---
            if not df_final.empty:
                st.subheader("📊 Distribución del Capital Inmovilizado")
                
                # Mapeamos los nombres completos para la leyenda
                df_grafico = df_final.groupby('Indicador ABC')['Importe disponible para acciones'].sum().reset_index()
                df_grafico['Categoría'] = df_grafico['Indicador ABC'].map(NOMENCLATURA).fillna(df_grafico['Indicador ABC'])
                
                # Mapa de colores (mantenemos consistencia)
                color_map = {v: '#ED1C24' if 'A' in v else '#333333' for v in NOMENCLATURA.values()}

                fig = px.pie(
                    df_grafico, values='Importe disponible para acciones', names='Categoría',
                    color='Categoría', color_discrete_map=color_map, hole=0.4
                )
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
                st.download_button(label="📥 Exportar Reporte de Acciones", data=output.getvalue(), file_name="Planilla_Overstock_Wurth.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)

        except Exception as e:
            st.error(f"Error en el análisis: {e}")
