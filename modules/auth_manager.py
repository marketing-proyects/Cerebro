import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

def gestionar_login():
    # Cargar configuración desde el YAML
    with open('config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)

    # Crear el objeto autenticador
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days']
    )

    # Renderizar el formulario de login
    # En versiones nuevas, el login no devuelve valores directamente
    authenticator.login(location='main')

    # Guardar el autenticador en el estado de la sesión para usar el logout luego
    st.session_state["authenticator"] = authenticator

    # Verificar el estado de autenticación desde el session_state
    if st.session_state["authentication_status"]:
        return True, st.session_state["username"]
    elif st.session_state["authentication_status"] is False:
        st.error('Usuario o contraseña incorrectos')
        return False, None
    else:
        st.warning('Por favor, ingrese su usuario y contraseña')
        return False, None
