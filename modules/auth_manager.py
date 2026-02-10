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

    # 3. Ejecutar el login
    # En versiones nuevas, esto ya no devuelve (name, status, username) directamente
    authenticator.login(location='main')

    # 4. Verificar el estado usando el session_state de Streamlit
    # Esto elimina el TypeError que ves en tu imagen
    if st.session_state.get("authentication_status"):
        authenticator.logout('Cerrar Sesión', 'sidebar')
        return True, st.session_state["username"]
    
    elif st.session_state.get("authentication_status") is False:
        st.error('Usuario o contraseña incorrectos')
        return False, None
    
    elif st.session_state.get("authentication_status") is None:
        st.warning('Por favor, ingrese sus credenciales.')
        return False, None
    
    return False, None
