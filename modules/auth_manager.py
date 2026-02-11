import streamlit as st
import os

def gestionar_login():
    # Definición de Usuarios y Permisos
    USUARIOS = {
        "admin": {"pass": "123", "modulos": ["Investigación de Mercado", "Fijación de Precios"]},
        "mkt_user": {"pass": "wurth2026", "modulos": ["Investigación de Mercado"]},
        "ventas_user": {"pass": "precios2026", "modulos": ["Fijación de Precios"]}
    }

    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        st.markdown("""
            <style>
            .stApp { background-color: #FFFFFF !important; }
            .login-header { display: flex; flex-direction: column; align-items: center; margin-top: 30px; margin-bottom: 20px; }
            div.stButton > button {
                background-color: #ED1C24 !important;
                color: white !important;
                font-weight: bold !important;
                width: 100% !important;
            }
            div.stButton > button p { color: white !important; }
            </style>
        """, unsafe_allow_html=True)

        st.markdown('<div class="login-header">', unsafe_allow_html=True)
        if os.path.exists("logo_wurth.png"):
            st.image("logo_wurth.png", width=200)
        else:
            st.markdown("<h1 style='color: #ED1C24;'>WÜRTH</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='color: #333333; margin-top: 10px;'>ACCESO CEREBRO</h3>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        with st.container():
            _, center_col, _ = st.columns([1, 2, 1])
            with center_col:
                with st.form(key="login_modular_v1"):
                    user = st.text_input("Usuario")
                    password = st.text_input("Contraseña", type="password")
                    if st.form_submit_button("INGRESAR"):
                        if user in USUARIOS and USUARIOS[user]["pass"] == password:
                            st.session_state["autenticado"] = True
                            st.session_state["username"] = user
                            st.session_state["permisos"] = USUARIOS[user]["modulos"]
                            st.rerun()
                        else:
                            st.error("Credenciales incorrectas")
        return False
    return True
