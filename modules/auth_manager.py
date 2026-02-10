import streamlit as st
import os

def gestionar_login():
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        st.markdown("""
            <style>
            .stApp { background-color: #FFFFFF !important; }
            .logo-login { display: flex; justify-content: center; margin-bottom: 20px; }
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

        st.markdown('<div class="logo-login">', unsafe_allow_html=True)
        # Priorizamos el logo oficial para asegurar visibilidad
        st.image("https://upload.wikimedia.org/wikipedia/commons/b/be/W%C3%BCrth_logo.svg", width=150)
        st.markdown('</div>', unsafe_allow_html=True)

        with st.container():
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                # El key único evita errores de duplicación
                with st.form(key="auth_v3"):
                    st.markdown("<h3 style='text-align: center; color: #ED1C24;'>ACCESO CEREBRO</h3>", unsafe_allow_html=True)
                    user = st.text_input("Usuario")
                    password = st.text_input("Contraseña", type="password")
                    if st.form_submit_button("INGRESAR"):
                        if user == "admin" and password == "123":
                            st.session_state["autenticado"] = True
                            st.session_state["username"] = user
                            st.rerun()
                        else:
                            st.error("Credenciales incorrectas")
        return False
    
    # IMPORTANTE: Solo devolvemos True sin imprimir nada
    return True
