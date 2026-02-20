import streamlit as st
import pandas as pd
import io
import plotly.express as px

def mostrar_matriz_decisiones():
    st.header("🎯 Matriz de Decisiones Estratégicas")
    st.info("Cruce de datos para optimizar la recuperación de capital y proteger el margen (GP) en Uruguay.")

    # 1. CARGA DE ARCHIVOS
    st.subheader("📁 Carga de Insumos")
    c_up1, c_up2 = st.columns(2)
    with c_up1:
        f_vto = st.file_uploader("Reporte de Vencimientos", type=['csv', 'xlsx'], key="vto_matrix")
    with c_up2:
        f_stk = st.file_uploader("Reporte de Sobre-stock", type=['csv', 'xlsx'], key="stk_matrix")

    if f_vto and f_stk:
        try:
            # Lectura de datos
            df_v = pd.read_csv(f_vto) if f_vto.name.endswith('.csv') else pd.read_excel(f_vto)
            df_s = pd.read_csv(f_stk) if f_stk.name.endswith('.csv') else pd.read_excel(f_stk)
            
            df_v.columns = df_v.columns.str.strip()
            df_s.columns = df_s.columns.str.strip()

            # Cruce de información por código de Material
            # Traemos Vencimiento y Estado de Riesgo del primer módulo
            df_total = pd.merge(df_s, df_v[['Material', 'Vencimiento en meses']], on='Material', how='inner')

            # --- LÓGICA DE LOS 4 CUADRANTES ---
            def definir_cuadrante(row):
                vto = float(row.get('Vencimiento en meses', 24))
                stk_meses = float(row.get('Meses de stock ATP', 0))
                
                if vto <= 6 and stk_meses >= 12:
                    return "🔴 CUADRANTE I: Liquidación Crítica (Doble Riesgo)"
                elif stk_meses >= 12:
                    return "🟠 CUADRANTE II: Despliegue Comercial (Riesgo Financiero)"
                elif vto <= 6:
                    return "🟡 CUADRANTE III: Venta Prioritaria (Riesgo Operativo)"
                else:
                    return "🟢 CUADRANTE IV: Optimización (Saludable)"

            df_total['Cuadrante'] = df_total.apply(definir_cuadrante, axis=1)

            # --- DASHBOARD DE ESTADO GENERAL ---
            st.markdown("---")
            st.subheader("📊 Estado de la Cartera de Inventario")
            
            dist_cuadrantes = df_total['Cuadrante'].value_counts().reset_index()
            fig_pie = px.pie(dist_cuadrantes, values='count', names='Cuadrante', 
                             color='Cuadrante', hole=0.4,
                             color_discrete_map={
                                 "🔴 CUADRANTE I: Liquidación Crítica (Doble Riesgo)": "#ED1C24",
                                 "🟠 CUADRANTE II: Despliegue Comercial (Riesgo Financiero)": "#FF8C00",
                                 "🟡 CUADRANTE III: Venta Prioritaria (Riesgo Operativo)": "#FFD700",
                                 "🟢 CUADRANTE IV: Optimización (Saludable)": "#228B22"
                             })
            st.plotly_chart(fig_pie, use_container_width=True)

            # --- SIMULADOR COMERCIAL POR CUADRANTE ---
            st.markdown("---")
            st.subheader("🛠️ Simulador de Oferta Comercial")
            
            seleccion = st.selectbox("Elegir Cuadrante para Accionar:", 
                                     options=sorted(df_total['Cuadrante'].unique()))
            
            df_sub = df_total[df_total['Cuadrante'] == seleccion].copy()

            if not df_sub.empty:
                # Métricas del Cuadrante
                m1, m2, m3 = st.columns(3)
                m1.metric("Items", len(df_sub))
                cap_exp = df_sub['VALOR STOCK'].sum() if 'VALOR STOCK' in df_sub.columns else 0
                m2.metric("Capital Expuesto", f"$ {cap_exp:,.0f}")
                
                # Input de Margen Objetivo
                gp_min = st.sidebar.slider("Piso de GP Objetivo (%)", 0, 100, 20)

                # --- EDITOR MANUAL DE PRECIOS ---
                st.write("📝 **Ajusta el 'Precio Promo' para calcular la rentabilidad:**")
                
                # Calculamos un precio base sugerido (por ejemplo, margen del 30% sobre costo)
                if 'PFEP' in df_sub.columns:
                    df_sub['Precio_Promo'] = df_sub['PFEP'] * 1.3
                else:
                    df_sub['Precio_Promo'] = 0.0

                df_editado = st.data_editor(
                    df_sub[['Material', 'Descripción del material', 'PFEP', 'ATP-quantity', 'Precio_Promo', 'Indicador ABC']],
                    column_config={
                        "Material": "Código",
                        "PFEP": st.column_config.NumberColumn("Costo (PFEP)", format="$ %.2f", disabled=True),
                        "ATP-quantity": st.column_config.NumberColumn("Stock", disabled=True),
                        "Precio_Promo": st.column_config.NumberColumn("Precio Promo (Editable)", format="$ %.2f", min_value=0.0),
                        "Indicador ABC": "Cat"
                    },
                    use_container_width=True,
                    hide_index=True
                )

                # --- CÁLCULOS EN TIEMPO REAL ---
                # GP Unitario = (Venta - Costo) / Venta
                df_editado['GP_Estimado'] = ((df_editado['Precio_Promo'] - df_editado['PFEP']) / df_editado['Precio_Promo']).fillna(0) * 100
                df_editado['Cash_In_Total'] = df_editado['Precio_Promo'] * df_editado['ATP-quantity']
                
                gp_promedio = df_editado['GP_Estimado'].mean()
                cash_total = df_editado['Cash_In_Total'].sum()

                # Visualización de resultados del simulador
                st.markdown("### 📈 Impacto de la Propuesta")
                r1, r2 = st.columns(2)
                
                color_gp = "normal" if gp_promedio >= gp_min else "inverse"
                r1.metric("GP Medio Ponderado", f"{gp_promedio:.2f}%", 
                          delta=f"{gp_promedio - gp_min:.1f}% vs Objetivo", delta_color=color_gp)
                r2.metric("Recuperación de Caja (Cash-In)", f"$ {cash_total:,.0f}")

                # Alerta si el GP es muy bajo
                if gp_promedio < gp_min:
                    st.warning(f"⚠️ La propuesta actual está por debajo del GP objetivo del {gp_min}%.")

                # --- EXCEL DE PROPUESTA ---
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df_editado.to_excel(writer, index=False, sheet_name='PropuestaComercial')
                
                st.download_button(
                    label="📥 Descargar Propuesta Comercial para Ventas",
                    data=output.getvalue(),
                    file_name=f"Propuesta_Cerebro_{seleccion[:12]}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )

        except Exception as e:
            st.error(f"Error al cruzar los reportes: {e}. Asegúrese de que ambos archivos tengan la columna 'Material'.")
    else:
        st.warning("Paso previo: Debes cargar ambos archivos para que Cerebro pueda cruzar el riesgo de tiempo (Vencimiento) con el riesgo de dinero (Sobre-stock).")
