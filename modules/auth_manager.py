import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

def cargar_configuracion():
    # En una fase avanzada, estos usuarios vendrán de una Base de Datos (ej. Supabase)
    # Por ahora, usamos un archivo config.yaml para definir usuarios
    with open('config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)
    return config

def gestionar_login():
    config = cargar_configuracion()

    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days']
    )

    # Renderiza el formulario de login en la UI
    name, authentication_status, username = authenticator.login('main')

    if authentication_status:
        st.session_state["authenticator"] = authenticator
        return True, username
    elif authentication_status is False:
        st.error('Usuario/Contraseña incorrectos')
        return False, None
    elif authentication_status is None:
        st.warning('Por favor, introduce tu usuario y contraseña')
        return False, None
