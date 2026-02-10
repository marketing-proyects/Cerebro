import streamlit as st
import pandas as pd
from modules.auth_manager import gestionar_login
from modules.data_processor import cargar_archivo, validar_columnas
from modules.ai_engine import procesar_investigacion_industrial

st.set_page_config(page_title="Cerebro", page_icon="🤖", layout="wide")

autenticado, usuario = gestionar_login()

if autenticado:
    st.sidebar.title(f"Usuario: {usuario}")
    st.title("🧠 Cerebro: Inteligencia de Mercado")
    
    df = cargar_archivo()
    if df is not None:
        cols = ["Nombre", "Especificación", "Material/Norma", "UE 1", "UE 2", "UE 3", "Precio Propio (Ref)", "URL Competidor"]
        if validar_columnas(df, cols):
            if st.button("🚀 Iniciar Escaneo Industrial"):
                with st.spinner("La IA está calculando empaques y T/C del BROU..."):
                    res = procesar_investigacion_industrial(df)
                
                df_res = pd.DataFrame(res)
                for _, r in df_res.iterrows():
                    if r["Es Oferta"]: st.warning(f"📢 **{r['Producto']}**: {r['Alerta']}")
                
                st.dataframe(df_res, use_container_width=True)
                st.download_button("📥 Descargar Excel", df_res.to_csv(index=False), "reporte.csv", "text/csv")
else:
    st.info("Por favor, ingrese sus credenciales.")
