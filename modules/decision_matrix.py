import streamlit as st
import pandas as pd
import io
import plotly.express as px

def mostrar_matriz_decisiones():
    st.header("🎯 Matriz de Decisiones Estratégicas")
    st.info("Cruce de datos para optimizar la recuperación de capital y proteger el margen (GP).")

    # 1. CARGA DE ARCHIVOS
    st.subheader("📁 Carga de Insumos")
    c_up1, c_up2 = st.columns(2)
    with c_up1:
        f_vto = st.file_uploader("Subir Reporte de Vencimientos", type=['csv', 'xlsx'], key="vto_matrix_v2")
    with c_up2:
        f_stk = st.file_uploader("Subir Reporte de Overstock (Valorizado)", type=['csv', 'xlsx'], key="stk_matrix_v2")

    if f_vto and f_stk:
        try:
            # Lectura de datos
            df_v = pd.read_csv(f_vto) if f_vto.name.endswith('.csv') else pd.read_excel(f_vto)
            df_s = pd.read_csv(f_stk) if f_stk.name.endswith('.csv') else pd.read_excel(f_stk)
            
            # --- LIMPIEZA CRÍTICA DE COLUMNAS Y DATOS ---
            df_v.columns = df_v.columns.str.strip()
            df_s.columns = df_s.columns.str.strip()

            # Aseguramos que 'Material' sea string y sin espacios para el cruce (Key de SAP)
            if 'Material' in df_v.columns and 'Material' in df_s.columns:
                df_v['Material'] = df_v['Material'].astype(str).str.strip()
                df_s['Material'] = df_s['Material'].astype(str).str.strip()
            else:
                st.error("❌ Error: Ambos archivos deben contener la columna 'Material'.")
                return

            # --- CRUCE DE DATOS ---
            # Unimos los datos. Solo traemos lo que necesitamos de Vencimientos
            cols_vto_necesarias = ['Material', 'Vencimiento en meses']
            # Verificamos si existe la columna de meses en el archivo de vto
            if 'Vencimiento en meses' not in df_v.columns:
                st.error("❌ El archivo de Vencimientos no tiene la columna 'Vencimiento en meses'. Genérelo primero en el módulo de Liquidación.")
                return

            df_total = pd.merge(df_s, df_v[cols_vto_necesarias], on='Material', how='inner')

            if df_total.empty:
                st.warning("⚠️ No se encontraron coincidencias entre ambos archivos. Verifique que los códigos de Material sean los mismos.")
                return

            # --- LÓGICA DE CUADRANTES ---
            def definir_cuadrante(row):
                # Usamos .get para evitar errores si la columna falta en una fila
                vto = float(row.get('Vencimiento en meses', 24))
                stk_meses = float(row.get('Meses de stock ATP', 0))
                
                if vto <= 6 and stk_meses >= 12:
                    return "🔴 CUADRANTE I: Liquidación Crítica"
                elif stk_meses >= 12:
                    return "🟠 CUADRANTE II: Riesgo Financiero"
                elif vto <= 6:
                    return "🟡 CUADRANTE III: Venta Prioritaria"
                else:
                    return "🟢 CUADRANTE IV: Optimización"

            df_total['Cuadrante'] = df_total.apply(definir_cuadrante, axis=1)

            # --- VISUALIZACIÓN ---
            st.markdown("---")
            st.subheader("📊 Distribución de Riesgos")
            
            dist_cuadrantes = df_total['Cuadrante'].value_counts().reset_index()
            dist_cuadrantes.columns = ['Cuadrante', 'Cantidad']
            
            fig_pie = px.pie(dist_cuadrantes, values='Cantidad', names='Cuadrante', 
                             hole=0.4, color='Cuadrante',
                             color_discrete_map={
                                 "🔴 CUADRANTE I: Liquidación Crítica": "#ED1C24",
                                 "🟠 CUADRANTE II: Riesgo Financiero": "#FF8C00",
                                 "🟡 CUADRANTE III: Venta Prioritaria": "#FFD700",
                                 "🟢 CUADRANTE IV: Optimización": "#228B22"
                             })
            st.plotly_chart(fig_pie, use_container_width=True)

            # --- SIMULADOR ---
            st.markdown("---")
            seleccion = st.selectbox("Elegir Cuadrante para Accionar:", sorted(df_total['Cuadrante'].unique()))
            df_sub = df_total[df_total['Cuadrante'] == seleccion].copy()

            if not df_sub.empty:
                # Normalizar columnas de dinero para el simulador
                col_costo = 'PFEP' if 'PFEP' in df_sub.columns else None
                if not col_costo:
                    st.error("❌ No se encuentra la columna de costo 'PFEP'.")
                    return

                # Parámetros del simulador
                with st.sidebar:
                    st.header("⚙️ Parámetros GP")
                    gp_min = st.slider("GP Objetivo (%)", 0, 100, 20)
                    st.divider()
                    st.write("Configura el margen mínimo que deseas defender.")

                # Preparar columnas para el editor
                df_sub['Precio_Promo'] = df_sub[col_costo] * 1.25 # Sugerencia inicial (25% margen)
                
                st.write(f"📝 **Editando {len(df_sub)} productos del {seleccion}:**")
                
                df_editado = st.data_editor(
                    df_sub[['Material', 'Descripción del material', col_costo, 'ATP-quantity', 'Precio_Promo', 'Indicador ABC']],
                    column_config={
                        "Material": "Código",
                        col_costo: st.column_config.NumberColumn("Costo (PFEP)", format="$ %.2f", disabled=True),
                        "ATP-quantity": st.column_config.NumberColumn("Stock", disabled=True),
                        "Precio_Promo": st.column_config.NumberColumn("Precio Promo (Editable)", format="$ %.2f", min_value=0.0),
                    },
                    use_container_width=True,
                    hide_index=True,
                    key="editor_matriz_v2"
                )

                # Cálculos finales
                df_editado['GP_Estimado'] = ((df_editado['Precio_Promo'] - df_editado[col_costo]) / df_editado['Precio_Promo']).fillna(0) * 100
                df_editado['Cash_In'] = df_editado['Precio_Promo'] * df_editado['ATP-quantity']
                
                m1, m2 = st.columns(2)
                gp_real = df_editado['GP_Estimado'].mean()
                color_gp = "normal" if gp_real >= gp_min else "inverse"
                
                m1.metric("GP Medio Ponderado", f"{gp_real:.1f}%", f"{gp_real - gp_min:.1f}% vs Meta", delta_color=color_gp)
                m2.metric("Recuperación de Caja", f"$ {df_editado['Cash_In'].sum():,.0f}")

                # Exportación
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df_editado.to_excel(writer, index=False, sheet_name='Propuesta')
                
                st.download_button("📥 Descargar Propuesta Comercial", output.getvalue(), 
                                   f"Propuesta_{seleccion[:10]}.xlsx", use_container_width=True)

        except Exception as e:
            st.error(f"Se produjo un error técnico: {e}")
    else:
        st.warning("Debe cargar ambos reportes para que la Matriz pueda cruzar la información.")
