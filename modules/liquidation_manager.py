import streamlit as st
import pandas as pd
import re

def mostrar_modulo_liquidation():
    st.header("📦 Módulo de Liquidación Estratégica")
    st.info("Diagnóstico de Inventario por Lote y Unidad de Empaque (UDE).")

    archivo = st.file_uploader("Cargar volcado de Vencimientos", type=['xlsx', 'csv'], key="liq_uploader_final")

    if archivo:
        try:
            df = pd.read_csv(archivo) if archivo.name.endswith('.csv') else pd.read_excel(archivo)
            df.columns = df.columns.str.strip()

            # --- TRATAMIENTO INTELIGENTE DE CÓDIGOS Y UE ---
            def procesar_codigo(txt):
                txt = str(txt).strip()
                # Buscamos el último número después de una serie de espacios
                # Ejemplo: "089001000 716    1" -> Raíz: "089001000 716", UDE: 1
                partes = re.split(r'\s{2,}', txt) 
                if len(partes) > 1:
                    raiz = partes[0].strip()
                    ude = partes[-1].strip()
                else:
                    # Si no hay espacios múltiples, tomamos el código tal cual y UDE 1 por defecto
                    raiz = txt
                    ude = "1"
                return pd.Series([raiz, ude])

            # Creamos dos nuevas columnas técnicas
            df[['Cod_Raiz', 'UDE']] = df['Material'].apply(procesar_codigo)

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

            # --- INTERFAZ ---
            st.subheader("🔍 Filtros de Inventario")
            f1, f2, f3 = st.columns(3)
            with f1:
                niveles = st.multiselect("Riesgo:", ["🔴 CRÍTICO", "🟡 ALERTA", "🟢 ESTABLE"], default=["🔴 CRÍTICO", "🟡 ALERTA"])
            with f2:
                # Buscador que ahora cruza Raíz, Descripción o Lote
                busqueda = st.text_input("Buscar (Código, Nombre o Lote):").strip()
            with f3:
                abc = sorted(df['Indicador A B C'].unique().tolist()) if 'Indicador A B C' in df.columns else []
                abc_sel = st.multiselect("ABC:", options=abc, default=abc)

            # Filtrado dinámico
            mask = df['Estado_Cerebro'].isin(niveles) & df['Indicador A B C'].isin(abc_sel)
            if busqueda:
                mask = mask & (df['Cod_Raiz'].str.contains(busqueda, case=False) | 
                               df['Descripción'].str.contains(busqueda, case=False) | 
                               df['Lote'].astype(str).str.contains(busqueda))
            
            df_final = df[mask].copy()

            # --- TABLA ---
            # Mostramos la UDE para que el usuario sepa cómo vienen empaquetados
            cols_ok = ['Estado_Cerebro', 'Cod_Raiz', 'Descripción', 'UDE', 'Lote', 'STOCK ATP', 'Vencimiento', 'Meses de stock', 'Indicador A B C']
            
            st.dataframe(
                df_final[cols_ok].sort_values(by=['Estado_Cerebro', 'Vencimiento']),
                use_container_width=True,
                hide_index=True
            )

            # Mensaje preventivo para el futuro módulo de ofertas
            if not df_final.empty:
                st.caption(f"💡 Se han detectado unidades de empaque (UDE) variables. El sistema respetará estos múltiplos para las futuras propuestas de ofertas.")

        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.info("Carga el archivo para analizar vencimientos y unidades de empaque.")
