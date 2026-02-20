import streamlit as st
import pandas as pd
import re

def mostrar_modulo_liquidation():
    st.header("📦 Módulo de Liquidación Estratégica")
    st.info("Diagnóstico de Inventario por Lote y Unidad de Empaque (UE).")

    archivo = st.file_uploader("Cargar volcado de Vencimientos", type=['xlsx', 'csv'], key="liq_uploader_v_final")

    if archivo:
        try:
            # 1. Lectura del archivo
            if archivo.name.endswith('.csv'):
                df = pd.read_csv(archivo)
            else:
                df = pd.read_excel(archivo)
            
            df.columns = df.columns.str.strip()

            # --- LIMPIEZA CRÍTICA DE TIPOS DE DATOS ---
            # Forzamos que estas columnas sean numéricas antes de cualquier operación
            #errors='coerce' convierte lo que no es número en NaN, luego fillna(0) lo hace 0
            cols_numericas = ['Vencimiento en meses', 'Meses de stock', 'STOCK ATP', 'Consumo mensual']
            for col in cols_numericas:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

            # --- TRATAMIENTO DE CÓDIGO Y UE ---
            def procesar_codigo_ue(txt):
                txt = str(txt).strip()
                partes = re.split(r'\s{2,}', txt)
                if len(partes) > 1:
                    raiz = partes[0].replace(" ", "")
                    ue = partes[-1]
                else:
                    raiz = txt.replace(" ", "")
                    ue = "1"
                return pd.Series([raiz, ue])

            df[['Cod_Limpio', 'UE']] = df['Material'].apply(procesar_codigo_ue)

            # --- LÓGICA DE SEMÁFORO ---
            def definir_estado(row):
                # Validamos 'Meses de acción' como texto
                accion = str(row.get('Meses de acción', '')).strip().lower()
                vto_m = row['Vencimiento en meses']
                stk_m = row['Meses de stock']
                
                if 'fecha vto' in accion or (stk_m > 0 and stk_m >= vto_m):
                    return "🔴 CRÍTICO"
                elif accion != 'ok' and stk_m > 0:
                    return "🟡 ALERTA"
                else:
                    return "🟢 ESTABLE"

            df['Estado_Cerebro'] = df.apply(definir_estado, axis=1)

            # --- FILTROS ---
            st.subheader("🔍 Filtros de Inventario")
            f1, f2, f3 = st.columns(3)
            with f1:
                niveles = st.multiselect("Estado de Riesgo:", 
                                       options=["🔴 CRÍTICO", "🟡 ALERTA", "🟢 ESTABLE"], 
                                       default=["🔴 CRÍTICO", "🟡 ALERTA"])
            with f2:
                busqueda = st.text_input("Buscar (Código, Nombre o Lote):").strip().replace(" ", "")
            with f3:
                abc_ops = sorted(df['Indicador A B C'].unique().tolist()) if 'Indicador A B C' in df.columns else []
                abc_sel = st.multiselect("Categoría ABC:", options=abc_ops, default=abc_ops)

            # --- APLICAR FILTRO ---
            mask = df['Estado_Cerebro'].isin(niveles) & df['Indicador A B C'].isin(abc_sel)
            if busqueda:
                mask = mask & (df['Cod_Limpio'].str.contains(busqueda, case=False) | 
                               df['Descripción'].str.contains(busqueda, case=False) |
                               df['Lote'].astype(str).str.contains(busqueda))
            
            df_final = df[mask].copy()

            # --- MÉTRICAS ---
            st.markdown("---")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Lotes en Análisis", len(df_final))
            m2.metric("Stock ATP", f"{int(df_final['STOCK ATP'].sum()):,}")
            m3.metric("Consumo Prom.", f"{df_final['Consumo mensual'].mean():.1f}")
            m4.metric("Meses Stock (Med.)", f"{df_final['Meses de stock'].median():.1f}")

            # --- TABLA DE ACCIÓN ---
            st.subheader("📋 Detalle de Criticidad y Empaque (UE)")
            
            cols_ver = [
                'Estado_Cerebro', 'Cod_Limpio', 'Descripción', 'UE', 'Lote', 
                'STOCK ATP', 'Vencimiento', 'Vencimiento en meses', 'Meses de stock', 'Indicador A B C'
            ]
            
            # Ordenamos asegurándonos de que no haya mezcla de tipos
            df_final = df_final.sort_values(by=['Estado_Cerebro', 'Vencimiento en meses'], ascending=[True, True])

            st.dataframe(
                df_final[cols_ver],
                use_container_width=True,
                hide_index=True
            )

        except Exception as e:
            st.error(f"Error al procesar el archivo: {e}")
            
    else:
        st.info("Carga el archivo de Vencimientos para analizar los lotes y sus unidades de empaque (UE).")
