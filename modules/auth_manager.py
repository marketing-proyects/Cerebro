import streamlit as st
import os

def gestionar_login():
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        # Estilos para centrar el logo y ocultar basura visual
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

        # Contenedor del Logo (usando tu archivo local)
        st.markdown('<div class="login-header">', unsafe_allow_html=True)
        
        # Intentamos cargar tu logo local
        if os.path.exists("logo_wurth.png"):
            st.image("logo_wurth.png", width=200)
        else:
            # Texto de respaldo si el archivo no está en la raíz
            st.markdown("<h1 style='color: #ED1C24;'>WÜRTH</h1>", unsafe_allow_html=True)
            
        st.markdown("<h3 style='color: #333333; margin-top: 10px;'>ACCESO CEREBRO</h3>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        with st.container():
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                with st.form(key="login_central_vFinal"):
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
