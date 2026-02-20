import streamlit as st
import pandas as pd
import io

def mostrar_matriz_decisiones():
    st.header("🎯 Matriz de Decisiones Estratégicas")
    st.info("Cruce de datos para optimizar la recuperación de capital y proteger el margen (GP).")

    # 1. CARGA DE DATOS (Requiere modulos Liquidacion x vencimiento & Overstock con información precargada para funcionar)
    col_u1, col_u2 = st.columns(2)
    with col_u1:
        file_vto = st.file_uploader("Subir Reporte de Vencimientos", type=['csv', 'xlsx'])
    with col_u2:
        file_stock = st.file_uploader("Subir Reporte de Sobre-stock (Valorizado)", type=['csv', 'xlsx'])

    if file_vto and file_stock:
        try:
            # Lectura y limpieza rápida
            df_vto = pd.read_csv(file_vto) if file_vto.name.endswith('.csv') else pd.read_excel(file_vto)
            df_stk = pd.read_csv(file_stock) if file_stock.name.endswith('.csv') else pd.read_excel(file_stock)
            
            df_vto.columns = df_vto.columns.str.strip()
            df_stk.columns = df_stk.columns.str.strip()

            # Merge por Código (Aseguramos que existan las columnas clave)
            # Nota: Usamos 'Material' como llave principal de SAP
            df_merge = pd.merge(df_stk, df_vto[['Material', 'Vencimiento en meses']], on='Material', how='inner')

            # --- LÓGICA DE CUADRANTES ---
            def asignar_cuadrante(row):
                vto = float(row.get('Vencimiento en meses', 24))
                meses_stk = float(row.get('Meses de stock ATP', 0))
                
                if vto <= 6 and meses_stk >= 12:
                    return "🔴 CUADRANTE I: Liquidación Crítica"
                elif meses_stk >= 12:
                    return "🟠 CUADRANTE II: Riesgo Financiero"
                elif vto <= 6:
                    return "🟡 CUADRANTE III: Venta Prioritaria"
                else:
                    return "🟢 CUADRANTE IV: Optimización"

            df_merge['Cuadrante'] = df_merge.apply(asignar_cuadrante, axis=1)

            # --- FILTROS DE LA MATRIZ ---
            st.subheader("🔍 Selección de Estrategia")
            cuadrante_sel = st.selectbox("Seleccionar Cuadrante para Accionar:", df_merge['Cuadrante'].unique())
            
            df_accion = df_merge[df_merge['Cuadrante'] == cuadrante_sel].copy()

            # --- SIMULADOR COMERCIAL ---
            st.markdown("### 🧮 Simulador de Oferta y Rentabilidad")
            st.write("Ajusta los valores para ver el impacto en el GP y la recuperación de capital.")

            # Parámetros Globales para la simulación
            with st.container(border=True):
                c1, c2, c3 = st.columns(3)
                with c1:
                    gp_objetivo = st.slider("GP Mínimo Objetivo (%)", 0, 100, 25)
                with c2:
                    st.metric("Items en Cuadrante", len(df_accion))
                with c3:
                    valor_original = df_accion['VALOR STOCK'].sum() if 'VALOR STOCK' in df_accion.columns else 0
                    st.metric("Capital Expuesto", f"$ {valor_original:,.0f}")

            # --- TABLA INTERACTIVA ---
            # Aquí el usuario puede ver el costo (PFEP) y proponer un precio
            st.write("#### Editor de Propuesta Comercial")
            
            # Preparar datos para edición
            # PFEP es el costo unitario
            df_accion['Precio_Venta_Actual'] = df_accion['PFEP'] / 0.6 # Estimación simple si no hay precio de venta
            df_accion['Precio_Promo_Sugerido'] = df_accion['Precio_Venta_Actual'] * 0.8 # Sugerencia inicial 20% off
            
            # Usamos st.data_editor para permitir ingreso manual
            df_editado = st.data_editor(
                df_accion[['Material', 'Descripción del material', 'PFEP', 'ATP-quantity', 'Precio_Promo_Sugerido', 'Indicador ABC']],
                column_config={
                    "PFEP": st.column_config.NumberColumn("Costo (PFEP)", format="$ %.2f", disabled=True),
                    "ATP-quantity": st.column_config.NumberColumn("Stock", disabled=True),
                    "Precio_Promo_Sugerido": st.column_config.NumberColumn("Precio Promo (MANUAL)", format="$ %.2f", min_value=0),
                },
                use_container_width=True,
                hide_index=True,
                key="editor_matriz"
            )

            # --- CÁLCULOS DE IMPACTO ---
            # GP Unitario = (Precio Promo - Costo) / Precio Promo
            df_editado['GP_Nuevo'] = ((df_editado['Precio_Promo_Sugerido'] - df_editado['PFEP']) / df_editado['Precio_Promo_Sugerido']) * 100
            df_editado['Recuperacion_Total'] = df_editado['Precio_Promo_Sugerido'] * df_editado['ATP-quantity']

            # Alertas de GP
            st.markdown("---")
            st.subheader("📈 Análisis de Impacto Final")
            
            res_col1, res_col2 = st.columns(2)
            
            with res_col1:
                gp_medio = df_editado['GP_Nuevo'].mean()
                color_gp = "normal" if gp_medio >= gp_objetivo else "inverse"
                st.metric("GP Promedio de la Acción", f"{gp_medio:.1f}%", delta=f"{gp_medio - gp_objetivo:.1f}% vs Objetivo", delta_color=color_gp)

            with res_col2:
                total_recuperado = df_editado['Recuperacion_Total'].sum()
                st.metric("Total Caja Estimado (Cash-In)", f"$ {total_recuperado:,.0f}")

            # Botón de Descarga
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df_editado.to_excel(writer, index=False, sheet_name='Propuesta_Comercial')
            
            st.download_button(
                label="📥 Descargar Propuesta para Ventas (Excel)",
                data=output.getvalue(),
                file_name=f"Propuesta_{cuadrante_sel.split(':')[0]}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

        except Exception as e:
            st.error(f"Error al cruzar los datos: {e}")
    else:
        st.info("Para activar la Matriz, por favor cargue ambos reportes (Vencimientos y Sobre-stock).")
