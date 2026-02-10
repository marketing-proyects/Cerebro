import streamlit as st
import requests
from io import BytesIO

def obtener_logo_seguro():
    """Descarga el logo y lo devuelve como bytes para evitar errores de renderizado"""
    url = "https://upload.wikimedia.org/wikipedia/commons/b/be/W%C3%BCrth_logo.svg"
    try:
        response = requests.get(url)
        return response.content
    except:
        return None

def gestionar_login():
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        # CSS para centrar el logo y ocultar el '0' fantasma
        st.markdown("""
            <style>
            .stApp { background-color: #FFFFFF !important; }
            .login-header {
                display: flex;
                flex-direction: column;
                align-items: center;
                margin-top: 30px;
                margin-bottom: 20px;
            }
            div.stButton > button {
                background-color: #ED1C24 !important;
                color: white !important;
                font-weight: bold !important;
                width: 100% !important;
            }
            div.stButton > button p { color: white !important; }
            </style>
        """, unsafe_allow_html=True)

        # Contenedor del Logo
        logo_data = obtener_logo_seguro()
        st.markdown('<div class="login-header">', unsafe_allow_html=True)
        if logo_data:
            st.image(logo_data, width=180)
        else:
            st.markdown("<h1 style='color: #ED1C24;'>WÜRTH</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='color: #333333; margin-top: 10px;'>ACCESO CEREBRO</h3>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        with st.container():
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                with st.form(key="login_central_final"):
                    user = st.text_input("Usuario")
                    password = st.text_input("Contraseña", type="password")
                    if st.form_submit_button("INGRESAR AL SISTEMA"):
                        if user == "admin" and password == "123":
                            st.session_state["autenticado"] = True
                            st.session_state["username"] = user
                            st.rerun()
                        else:
                            st.error("Credenciales incorrectas")
        return False
    return True
