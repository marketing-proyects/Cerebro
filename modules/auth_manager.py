import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

def gestionar_login():
    # 1. Cargar configuración
    try:
        with open('config.yaml') as file:
            config = yaml.load(file, Loader=SafeLoader)
    except Exception as e:
        st.error(f"Error al cargar config.yaml: {e}")
        return False, None

    # 2. Inicializar el autenticador
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days']
    )

    # 3. Renderizar el formulario (esta es la parte que causaba el TypeError)
    # En las versiones nuevas, login() maneja el estado internamente
    authenticator.login(location='main')

    # 4. Validar el acceso usando el estado de la sesión
    if st.session_state["authentication_status"]:
        authenticator.logout('Cerrar Sesión', 'sidebar')
        return True, st.session_state["username"]
    
    elif st.session_state["authentication_status"] is False:
        st.error('Usuario o contraseña incorrectos')
        return False, None
    
    elif st.session_state["authentication_status"] is None:
        st.warning('Por favor, ingrese su usuario y contraseña')
        return False, None
    
    return False, None
