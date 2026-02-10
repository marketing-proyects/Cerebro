import streamlit as st
import os

def gestionar_login():
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        # CSS para limpiar la interfaz y arreglar el botón
        st.markdown("""
            <style>
            /* Evitar que el fondo se rompa */
            .stApp { background-color: #FFFFFF !important; }
            
            /* Logo centrado sin duplicados visuales */
            .logo-login { display: flex; justify-content: center; margin-bottom: 20px; }
            
            /* BOTÓN INGRESAR: Fondo Rojo Würth, Texto Blanco */
            div.stButton > button {
                background-color: #ED1C24 !important;
                color: white !important;
                border: none !important;
                font-weight: bold !important;
                width: 100% !important;
            }
            div.stButton > button p { color: white !important; }
            </style>
        """, unsafe_allow_html=True)

        # Mostrar logo solo una vez
        st.markdown('<div class="logo-login">', unsafe_allow_html=True)
        # Probamos con tu logo local primero
        if os.path.exists("logo_wurth.png"):
            st.image("logo_wurth.png", width=150)
        else:
            st.image("https://upload.wikimedia.org/wikipedia/commons/b/be/W%C3%BCrth_logo.svg", width=150)
        st.markdown('</div>', unsafe_allow_html=True)

        # Usamos un contenedor único para evitar el error de duplicado
        with st.container():
            # El error "StreamlitAPIException" se evita asegurando que este bloque sea único
            with st.form(key="auth_form_unique"):
                st.markdown("<h3 style='text-align: center; color: #ED1C24;'>ACCESO AL SISTEMA</h3>", unsafe_allow_html=True)
                user = st.text_input("Usuario")
                password = st.text_input("Contraseña", type="password")
                submit = st.form_submit_button("INGRESAR")

                if submit:
                    if user == "admin" and password == "123":
                        st.session_state["autenticado"] = True
                        st.session_state["username"] = user
                        st.rerun()
                    else:
                        st.error("Usuario o contraseña incorrectos")
        return False
    return True
