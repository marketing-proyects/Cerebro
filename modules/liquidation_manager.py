import streamlit as st
import pandas as pd
import re

def mostrar_modulo_liquidation():
    st.header("📦 Módulo de Liquidación Estratégica")
    st.info("Diagnóstico de Inventario por Lote y Unidad de Empaque (UE).")

    # 1. Carga de archivo
    archivo = st.file_uploader("Cargar volcado de Vencimientos", type=['xlsx', 'csv'], key="liq_uploader_v5")

    if archivo:
        try:
            # Lectura del archivo
            df = pd.read_csv(archivo) if archivo.name.endswith('.csv') else pd.read_excel(archivo)
            df.columns = df.columns.str.strip()

            # --- TRATAMIENTO DE CÓDIGO Y UE ---
            def procesar_codigo_ue(txt):
                txt = str(txt).strip()
                # Separamos por espacios múltiples (2 o más) 
                # El último bloque después de los espacios es la UE
                partes = re.split(r'\s{2,}', txt)
                if len(partes) > 1:
                    # Raíz: lo primero (quitamos espacios internos por si acaso)
                    # UE: lo último
                    raiz = partes[0].replace(" ", "")
                    ue = partes[-1]
                else:
                    raiz = txt.replace(" ", "")
                    ue = "1" # Default si no hay espacios múltiples
                return pd.Series([raiz, ue])

            # Aplicamos la extracción
            df[['Cod_Limpio', 'UE']] = df['Material'].apply(procesar_codigo_ue)

            # --- LÓGICA DE SEMÁFORO ---
            def definir_estado(row):
                accion = str(row.get('Meses de acción', '')).strip().lower()
                vto_m = pd.to_numeric(row.get('Vencimiento en meses', 0), errors='coerce')
                stk_m = pd.to_numeric(row.get('Meses de stock', 0), errors='coerce')
                
                if 'fecha vto' in accion or (stk_m > 0 and stk_m >= vto_m):
                    return "🔴 CRÍTICO"
                elif accion != 'ok' and stk_m > 0:
                    return "🟡 ALERTA"
                else:
                    return "🟢 ESTABLE"

            df['Estado_Cerebro'] = df.apply(definir_estado, axis=1)

            # --- INTERFAZ DE FILTROS ---
            st.subheader("🔍 Filtros de Inventario")
            f1, f2, f3 = st.columns(3)
            with f1:
                niveles = st.multiselect("Nivel de Riesgo:", ["🔴 CRÍTICO", "🟡 ALERTA", "🟢 ESTABLE"], default=["🔴 CRÍTICO", "🟡 ALERTA"])
            with f2:
                # El buscador ahora limpia los espacios del usuario para coincidir con Cod_Limpio
                busqueda = st.text_input("Buscar (Código, Nombre o Lote):").strip().replace(" ", "")
            with f3:
                abc = sorted(df['Indicador A B C'].unique().tolist()) if 'Indicador A B C' in df.columns else []
                abc_sel = st.multiselect("Categoría ABC:", options=abc, default=abc)

            # Filtrado
            mask = df['Estado_Cerebro'].isin(niveles) & df['Indicador A B C'].isin(abc_sel)
            if busqueda:
                mask = mask & (df['Cod_Limpio'].str.contains(busqueda, case=False) | 
                               df['Descripción'].str.contains(busqueda, case=False) |
                               df['Lote'].astype(str).str.contains(busqueda))
            
            df_final = df[mask].copy()

            # --- TABLA DE RESULTADOS ---
            st.subheader("📋 Detalle de Lotes y Empaques (UE)")
            
            cols_ver = [
                'Estado_Cerebro', 'Cod_Limpio', 'Descripción', 'UE', 'Lote', 
                'STOCK ATP', 'Vencimiento', 'Meses de stock', 'Indicador A B C'
            ]
            
            st.dataframe(
                df_final[cols_ver].sort_values(by=['Estado_Cerebro', 'Vencimiento']),
                use_container_width=True,
                hide_index=True
            )

            if not df_final.empty:
                st.info(f"💡 Se han identificado {len(df_final)} registros. El sistema ha normalizado los códigos y extraído la UE para futuras acciones comerciales.")

        except Exception as e:
            st.error(f"Error al procesar el archivo: {e}")
    else:
        st.info("Carga el reporte de vencimientos para analizar la criticidad y las UE.")
