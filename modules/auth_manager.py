import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

def gestionar_login():
    try:
        with open('config.yaml') as file:
            config = yaml.load(file, Loader=SafeLoader)
    except Exception as e:
        st.error(f"Error al cargar config.yaml: {e}")
        return

    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days']
    )

    # Corregido: La ubicación ('main') debe ser el primer argumento
    authenticator.login(location='main')
