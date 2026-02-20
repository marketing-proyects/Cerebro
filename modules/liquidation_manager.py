import streamlit as st
import pandas as pd
import numpy as np

def mostrar_modulo_liquidation():
    st.header("📦 Módulo de Liquidación Estratégica")
    st.info("Análisis de criticidad basado en Vencimiento vs. Capacidad de Venta (Sell-out).")

    archivo = st.file_uploader("Cargar volcado de Vencimientos (Excel/CSV)", type=['xlsx', 'csv'], key="liq_uploader_real")

    if archivo:
        try:
            # Lectura del nuevo formato
            if archivo.name.endswith('.csv'):
                df = pd.read_csv(archivo)
            else:
                df = pd.read_excel(archivo)

            # 1. LIMPIEZA DE DATOS (Nombres de columnas y espacios)
            df.columns = df.columns.str.strip()
            # Limpiar espacios en blanco de los códigos de material para que no fallen las búsquedas
            df['Material'] = df['Material'].astype(str).str.strip()

            # 2. LÓGICA DEL FACTOR CRÍTICO (Semáforo Dinámico)
            def calcular_semaforo(row):
                try:
                    vto_meses = float(row['Vencimiento en meses'])
                    stock_meses = float(row['Meses de stock'])
                    
                    if stock_meses >= vto_meses:
                        return "🔴 CRÍTICO (Liquidar)"
                    elif vto_meses - stock_meses <= 3: # Margen de seguridad de 3 meses
                        return "🟡 MEDIO (Promocionar)"
                    else:
                        return "🟢 OK"
                except:
                    return "⚪ Sin Datos"

            df['Semaforo_Cerebro'] = df.apply(calcular_semaforo, axis=1)

            # --- PANEL DE FILTROS ---
            st.subheader("🔍 Filtros de Acción")
            f1, f2, f3 = st.columns(3)
            with f1:
                nivel = st.multiselect("Nivel de Agresividad:", 
                                     options=df['Semaforo_Cerebro'].unique(), 
                                     default=["🔴 CRÍTICO (Liquidar)", "🟡 MEDIO (Promocionar)"])
            with f2:
                cat_abc = st.multiselect("Categoría ABC:", options=sorted(df['Indicador A B C'].unique()), default=['A', 'B'])
            with f3:
                busqueda = st.text_input("Buscar por Material o Lote:")

            # Aplicar Filtros
            mask = (df['Semaforo_Cerebro'].isin(nivel)) & (df['Indicador A B C'].isin(cat_abc))
            if busqueda:
                mask = mask & (df['Material'].str.contains(busqueda) | df['Descripción'].str.contains(busqueda, case=False))
            
            df_filtrado = df[mask]

            # --- MÉTRICAS ---
            st.markdown("---")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Items a Liquidar", len(df_filtrado))
            m2.metric("Stock ATP Total", f"{int(df_filtrado['STOCK ATP'].sum()):,}")
            # Calculamos valorización estimada si tuvieramos el PPP, por ahora cantidad
            m3.metric("Lotes en Riesgo", df_filtrado['Lote'].nunique())
            m4.metric("Meses Stock Prom.", f"{df_filtrado['Meses de stock'].mean():.1f}")

            # --- TABLA DE DATOS ---
            st.subheader("📋 Detalle de Lotes y Vencimientos")
            
            # Seleccionamos las columnas útiles para el usuario
            cols_mostrar = [
                'Semaforo_Cerebro', 'Material', 'Descripción', 'Lote', 
                'STOCK ATP', 'Vencimiento', 'Vencimiento en meses', 
                'Meses de stock', 'Indicador A B C'
            ]
            
            st.dataframe(
                df_filtrado[cols_mostrar].sort_values(by='Vencimiento'),
                use_container_width=True,
                hide_index=True
            )

            # --- ESTRATEGIA DE OFERTAS ---
            st.markdown("---")
            st.subheader("📢 Recomendación de Ofertas")
            
            c_agresiva, c_moderada = st.columns(2)
            with c_agresiva:
                st.error("🔥 **Oferta AGRESIVA (Rojos)**")
                st.write("""
                - **Tipo:** Liquidación por vencimiento inminente.
                - **Acción:** Descuento directo > 40% o Pack 2x1.
                - **Objetivo:** Recuperar costo antes del vencimiento total.
                """)
            with c_moderada:
                st.warning("⚡ **Oferta MODERADA (Amarillos)**")
                st.write("""
                - **Tipo:** Acción preventiva de Overstock.
                - **Acción:** Combo con productos Clase A o 20% de descuento por volumen.
                - **Objetivo:** Acelerar el sell-out para evitar que pasen a Rojo.
                """)

        except Exception as e:
            st.error(f"Error al analizar el nuevo formato: {e}")
            st.info("Asegúrate de cargar el archivo con las columnas: Material, Lote, STOCK ATP, Vencimiento en meses, etc.")
    else:
        st.info("Carga el reporte de vencimientos para determinar la agresividad de las ofertas.")
