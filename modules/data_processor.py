import pandas as pd
import streamlit as st

def cargar_archivo():
    """Maneja la subida del archivo Excel por parte del usuario"""
    uploaded_file = st.file_uploader("Sube tu Ficha Técnica de Productos (Excel)", type=['xlsx'])
    
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
    """Verifica que el Excel tenga la estructura técnica industrial"""
    columnas_actuales = [str(col).strip() for col in df.columns]
    faltantes = [col for col in columnas_requeridas if col not in columnas_actuales]
    
    if faltantes:
        st.error(f"Estructura inválida. Faltan las columnas: {', '.join(faltantes)}")
        st.info("Asegúrate de usar: Nombre, Especificación, Material/Norma, UE 1, UE 2, UE 3, Precio Propio (Ref), URL Competidor")
        return False
    return True
