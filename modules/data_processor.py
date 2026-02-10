import pandas as pd
import streamlit as st

def cargar_archivo():
    """Maneja la subida del archivo Excel por parte del usuario"""
    uploaded_file = st.file_uploader("Sube tu lista de productos (Excel)", type=['xlsx'])
    
    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)
            st.success("✅ Archivo cargado correctamente")
            return df
        except Exception as e:
            st.error(f"Error al leer el archivo: {e}")
            return None
    return None

def validar_columnas(df, columnas_requeridas):
    """Verifica que el Excel tenga los títulos que necesitamos"""
    columnas_actuales = set(df.columns)
    faltantes = [col for col in columnas_requeridas if col not in columnas_actuales]
    
    if faltantes:
        st.warning(f"Faltan las siguientes columnas: {', '.join(faltantes)}")
        return False
    return True
