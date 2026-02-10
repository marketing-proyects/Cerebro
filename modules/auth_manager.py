import streamlit as st
import base64
import requests

def gestionar_login():
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        # Estilos mejorados
        st.markdown("""
            <style>
            .stApp { background-color: #FFFFFF !important; }
            .login-wrapper {
                text-align: center;
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

        # URL del logo
        url_logo = "https://upload.wikimedia.org/wikipedia/commons/b/be/W%C3%BCrth_logo.svg"
        
        # Insertar el logo usando un iframe o imagen directa con estilo inline para asegurar visibilidad
        st.markdown(f"""
            <div class="login-wrapper">
                <img src="{url_logo}" width="200">
                <h2 style='color: #ED1C24; font-family: Helvetica, Arial, sans-serif;'>ACCESO CEREBRO</h2>
            </div>
        """, unsafe_allow_html=True)
        
        with st.container():
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                with st.form(key="login_form_vfinal"):
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
