import streamlit as st
import pandas as pd
import re
import io
import plotly.express as px

def mostrar_modulo_overstock():
    st.header("📊 Gestión de Sobre-stock y Recuperación de Capital")
    st.info("Identificación de capital inmovilizado y riesgo de pérdida contable.")

    # --- BLOQUE DE AYUDA 1: Categorías (Quién es el producto) ---
    with st.expander("ℹ️ 1. LEYENDA DE CATEGORÍAS (ABC/DEGN)"):
        st.markdown("""
        | Cat | Descripción | Estrategia para Recuperar Capital |
        | :--- | :--- | :--- |
        | **A** | **Alta Rotación:** Capital seguro. | No liquidar. Frenar compras hasta normalizar stock. |
        | **B** | **Media Rotación:** Capital estable. | Promover venta cruzada (Cross-selling). |
        | **C** | **Baja Rotación:** Capital lento. | Ofertas especiales para liberar espacio en depósito. |
        | **D** | **Residual:** Capital estancado. | **Acción Agresiva:** Recuperar el costo (Cash-out). |
        | **E** | **Exhibidores:** Activos de Mkt. | Sacar del depósito y enviar a clientes estratégicos. |
        | **G** | **Gifts / Regalos:** Costo hundido. | Usar como 'gancho' para vender productos C/D. |
        | **N** | **Nuevos:** Lanzamientos. | Evaluar si el mercado aceptó el producto. |
        """)

    # --- BLOQUE DE AYUDA 2: Semáforo (Qué tan grave es su stock) ---
    with st.expander("🚦 2. LÓGICA DEL SEMÁFORO (Meses de Stock)"):
        st.markdown("""
        | Estado | Condición | Riesgo Contable |
        | :--- | :--- | :--- |
        | 🔴 **RIESGO CONTABLE** | > 12 meses de stock | **Muy Alto:** El capital está "dormido" hace más de un año. |
        | ⚪ **SIN ROTACIÓN** | Stock > 0 y Venta = 0 | **Extremo:** No hay inercia de venta. Peligro de pérdida total. |
        | 🟡 **EXCEDENTE** | 6 a 12 meses de stock | **Medio:** Stock por encima de la media de seguridad. |
        | 🟢 **SALUDABLE** | < 6 meses de stock | **Bajo:** El producto rota dentro de los parámetros normales. |
        """)

    archivo = st.file_uploader("Cargar reporte de Sobre-stock (Overstock)", type=['xlsx', 'csv'], key="overstock_final_full")

    if archivo:
        try:
            df = pd.read_csv(archivo) if archivo.name.endswith('.csv') else pd.read_excel(archivo)
            df.columns = df.columns.str.strip()

            # --- LIMPIEZA DE DATOS ---
            cols_num = ['ATP-quantity', 'Meses de stock ATP', 'Importe disponible para acciones', 'Promedio de venta mensual']
            for col in cols_num:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(float)

            df['Indicador ABC'] = df['Indicador ABC'].astype(str).replace('nan', 'S/D').str.strip() if 'Indicador ABC' in df.columns else 'S/D'

            # --- TRATAMIENTO DE CÓDIGO Y UE ---
            def procesar_ue(txt):
                txt = str(txt).strip()
                partes = re.split(r'\s{2,}', txt)
                raiz = partes[0].replace(" ", "") if len(partes) > 1 else txt.replace(" ", "")
                ue = partes[-1] if len(partes) > 1 else "1"
                return pd.Series([raiz, ue])

            df[['Cod_Limpio', 'UE']] = df['Material'].apply(procesar_ue)

            # --- LÓGICA DE SEMÁFORO FINANCIERO ---
            def definir_salud(row):
                if row['ATP-quantity'] > 0 and row['Promedio de venta mensual'] == 0:
                    return "⚪ SIN ROTACIÓN"
                elif row['Meses de stock ATP'] > 12:
                    return "🔴 RIESGO CONTABLE"
                elif row['Meses de stock ATP'] >= 6:
                    return "🟡 EXCEDENTE"
                else:
                    return "🟢 SALUDABLE"

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

            # --- MÉTRICAS DE VALOR ---
            st.markdown("---")
            m1, m2, m3 = st.columns(3)
            m1.metric("Lotes en Riesgo", len(df_final))
            cap_inv = df_final['Importe disponible para acciones'].sum()
            m2.metric("Capital Inmovilizado", f"$ {cap_inv:,.0f}")
            m3.metric("Recuperación Potencial (50%)", f"$ {(cap_inv * 0.5):,.0f}")

            # --- GRÁFICO DE TORTA: DISTRIBUCIÓN DE CAPITAL ---
            if not df_final.empty:
                st.subheader("📊 Distribución del Capital Inmovilizado")
                df_grafico = df_final.groupby('Indicador ABC')['Importe disponible para acciones'].sum().reset_index()
                
                colores = {'A': '#ED1C24', 'B': '#333333', 'C': '#555555', 'D': '#888888', 'E': '#AAAAAA', 'G': '#CCCCCC', 'N': '#EEEEEE', 'S/D': '#000000'}

                fig = px.pie(
                    df_grafico, values='Importe disponible para acciones', names='Indicador ABC',
                    color='Indicador ABC', color_discrete_map=colores, hole=0.4
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True)

            # --- TABLA DE RESULTADOS ---
            st.subheader("📋 Detalle de Artículos Estancados")
            cols_ver = ['Salud_Inventario', 'Cod_Limpio', 'Descripción del material', 'UE', 'ATP-quantity', 'Meses de stock ATP', 'Importe disponible para acciones', 'Indicador ABC']
            df_final = df_final.sort_values(by='Importe disponible para acciones', ascending=False)
            st.dataframe(df_final[cols_ver], use_container_width=True, hide_index=True)

            # --- DESCARGA ---
            if not df_final.empty:
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df_final[cols_ver].to_excel(writer, index=False, sheet_name='Overstock')
                
                st.download_button(
                    label="📥 Exportar Reporte de Acciones Comerciales",
                    data=output.getvalue(),
                    file_name="Planilla_Overstock_Wurth.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )

        except Exception as e:
            st.error(f"Error en el análisis: {e}")
    else:
        st.info("Suba el reporte de stock para identificar el capital inmovilizado.")
