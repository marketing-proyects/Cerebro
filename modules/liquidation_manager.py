import streamlit as st
import pandas as pd
import re

def mostrar_modulo_liquidation():
    st.header("📦 Módulo de Liquidación Estratégica")
    st.info("Diagnóstico de Inventario por Lote y Unidad de Empaque (UE). Este módulo no utiliza IA.")

    archivo = st.file_uploader("Cargar volcado de Vencimientos", type=['xlsx', 'csv'], key="liq_uploader_v_final")

    if archivo:
        try:
            # 1. Lectura del archivo
            if archivo.name.endswith('.csv'):
                df = pd.read_csv(archivo)
            else:
                df = pd.read_excel(archivo)
            
            # Limpiar nombres de columnas (quitar espacios en los encabezados)
            df.columns = df.columns.str.strip()

            # --- LIMPIEZA AGRESIVA DE DATOS ---
            
            # A. Columnas Numéricas: Forzamos a float y convertimos errores (como "Ok" o "Fecha vto") en 0
            cols_a_limpiar = ['Vencimiento en meses', 'Meses de stock', 'STOCK ATP', 'Consumo mensual']
            for col in cols_a_limpiar:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(float)

            # B. Columna ABC: La "vacunamos" contra errores de tipo (NaN vs Str)
            if 'Indicador A B C' in df.columns:
                # CORRECCIÓN: Usamos .str.strip() para Series de Pandas
                df['Indicador A B C'] = df['Indicador A B C'].astype(str).replace('nan', 'S/D').str.strip()
            else:
                df['Indicador A B C'] = 'S/D'

            # --- TRATAMIENTO DE CÓDIGO Y UE ---
            def procesar_codigo_ue(txt):
                txt = str(txt).strip()
                # Separar por espacios múltiples (2 o más) para encontrar la UE al final
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
                accion_txt = str(row.get('Meses de acción', '')).strip().lower()
                vto_val = float(row['Vencimiento en meses'])
                stk_val = float(row['Meses de stock'])
                
                # Criterio Würth: Si el sistema ya dice "vto" o si el stock dura más que la vida útil
                if 'vto' in accion_txt or (stk_val > 0 and stk_val >= vto_val):
                    return "🔴 CRÍTICO"
                elif 'ok' not in accion_txt and stk_val > 0:
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
                # El buscador limpia espacios para coincidir con la raíz del código
                busqueda = st.text_input("Buscar (Código, Nombre o Lote):").strip().replace(" ", "")
            with f3:
                # Creamos la lista de opciones ABC de forma segura (solo strings únicos)
                abc_ops = sorted([str(x) for x in df['Indicador A B C'].unique() if str(x) != 'nan'])
                abc_sel = st.multiselect("Categoría ABC:", options=abc_ops, default=abc_ops)

            # --- APLICAR FILTRO ---
            mask = df['Estado_Cerebro'].isin(niveles) & df['Indicador A B C'].isin(abc_sel)
            if busqueda:
                mask = mask & (df['Cod_Limpio'].str.contains(busqueda, case=False) | 
                               df['Descripción'].str.contains(busqueda, case=False) |
                               df['Lote'].astype(str).str.contains(busqueda))
            
            df_final = df[mask].copy()

            # --- TABLA DE ACCIÓN ---
            st.subheader("📋 Detalle de Criticidad y Empaque (UE)")
            
            cols_ver = [
                'Estado_Cerebro', 'Cod_Limpio', 'Descripción', 'UE', 'Lote', 
                'STOCK ATP', 'Vencimiento', 'Vencimiento en meses', 'Meses de stock', 'Indicador A B C'
            ]
            
            # Ordenamos asegurando que no haya tipos mezclados
            df_final = df_final.sort_values(by=['Estado_Cerebro', 'Vencimiento en meses'], ascending=[True, True])

            st.dataframe(
                df_final[cols_ver],
                use_container_width=True,
                hide_index=True
            )

        except Exception as e:
            st.error(f"Error al procesar el archivo: {e}")
            
    else:
        st.info("Carga el reporte de vencimientos para analizar los lotes y sus unidades de empaque (UE).")
