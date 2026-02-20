import streamlit as st
import pandas as pd
import os

def mostrar_modulo_liquidation():
    st.header("📦 Módulo de Liquidación Estratégica")
    st.info("Este módulo analiza el stock con próximo vencimiento para facilitar la toma de decisiones comerciales. Este módulo no tiene conección con IA")

    # 1. Carga de archivo aislada para este módulo
    archivo = st.file_uploader("Cargar planilla 'Vencimientos'", type=['xlsx', 'csv'], key="liq_uploader")

    if archivo:
        try:
            # Lectura del archivo (CSV o Excel)
            if archivo.name.endswith('.csv'):
                # Saltamos la primera fila de metadata si existe
                df = pd.read_csv(archivo, skiprows=1)
            else:
                df = pd.read_excel(archivo, sheet_name='Vencimientos', skiprows=1)

            # Limpieza: Eliminar columnas completamente vacías
            df = df.dropna(axis=1, how='all')

            # --- FILTROS LATERALES / SUPERIORES ---
            st.subheader("🔍 Filtros de Inventario")
            c1, c2, c3 = st.columns(3)
            
            with c1:
                # Obtenemos los niveles de riesgo únicos (ALTO, MEDIO, OK, etc.)
                opciones_riesgo = df['Riesgo'].unique().tolist() if 'Riesgo' in df.columns else []
                riesgos_sel = st.multiselect("Nivel de Riesgo:", opciones_riesgo, default=[r for r in opciones_riesgo if 'ALTO' in str(r)])

            with c2:
                # Filtro por texto para descripción o código
                busqueda = st.text_input("Buscar producto (Código o Nombre):")

            with c3:
                stock_min = st.number_input("Stock mínimo:", value=0)

            # --- APLICAR FILTROS ---
            mask = (df['Riesgo'].isin(riesgos_sel)) & (df['Stock'].astype(float) >= stock_min)
            if busqueda:
                mask = mask & (df['Descripcion'].str.contains(busqueda, case=False) | df['Codigo'].str.contains(busqueda))
            
            df_final = df[mask]

            # --- MÉTRICAS DE RESUMEN ---
            st.markdown("---")
            m1, m2, m3, m4 = st.columns(4)
            
            items_riesgo = len(df_final)
            total_unidades = int(df_final['Stock'].sum()) if 'Stock' in df_final.columns else 0
            unidades_riesgo = int(df_final['Unidades en riesgo'].sum()) if 'Unidades en riesgo' in df_final.columns else 0
            
            m1.metric("SKUs en Riesgo", items_riesgo)
            m2.metric("Stock Físico", total_unidades)
            m3.metric("Unidades en Riesgo", unidades_riesgo, delta_color="inverse")
            m4.metric("Días Prom. Agote", f"{int(df_final['Días para Agotar'].mean()) if 'Días para Agotar' in df_final.columns else 0} d")

            # --- TABLA DE ACCIÓN ---
            st.subheader("📋 Listado de Productos para Acción Comercial")
            
            # Formateamos la tabla para que sea legible
            columnas_ver = ['Codigo', 'Descripcion', 'Stock', 'Vencimiento', 'Días para Agotar', 'Riesgo', 'Aceleración de lote']
            # Solo mostramos las columnas que realmente existan en el archivo
            columnas_existentes = [c for c in columnas_ver if c in df_final.columns]
            
            st.dataframe(
                df_final[columnas_existentes].sort_values(by='Vencimiento', ascending=True),
                use_container_width=True,
                hide_index=True
            )

            # --- SECCIÓN DE ESTRATEGIA MANUAL ---
            st.markdown("---")
            st.subheader("💡 Estrategia Sugerida (Basada en Semáforo)")
            
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.error("**Acción Inmediata (Riesgo ALTO):**")
                st.write("- Liquidación agresiva al costo.\n- Packs de regalo por compras de volumen.\n- Comunicación directa a toda la fuerza de ventas.")
            
            with col_b:
                st.warning("**Acción Preventiva (Riesgo MEDIO):**")
                st.write("- Descuentos escalonados.\n- Inclusión en combos de productos 'A'.\n- Monitoreo semanal de rotación.")

        except Exception as e:
            st.error(f"Error al procesar los datos: {e}")
            st.info("Asegúrate de que el archivo tenga la pestaña 'Vencimientos' con las columnas correspondientes.")
    else:
        st.info("Esperando carga de planilla para analizar stock...")
