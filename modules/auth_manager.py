import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

def gestionar_login():
    with open('config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)

    # Inicializar el autenticador con la estructura exacta del YAML
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days']
    )

    # Renderizar el formulario de login
    # Nota: El nombre del usuario en el YAML debe ser 'admin'
    name, authentication_status, username = authenticator.login('main')

    if authentication_status:
        return True, username
    elif authentication_status == False:
        st.error('Usuario o contraseña incorrectos')
        return False, None
    elif authentication_status == None:
        st.warning('Por favor, ingrese su usuario y contraseña')
        return False, None
