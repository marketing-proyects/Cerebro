import streamlit as st

def gestionar_login():
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        st.markdown("""
            <style>
            /* Botón de Login Sólido */
            div.stButton > button {
                background-color: #ED1C24 !important;
                color: black !important;
                border: red !important;
                height: 3em !important;
                width: 100% !important;
            }
            </style>
        """, unsafe_allow_html=True)
        
        st.markdown("<h2 style='text-align: center; color: #ED1C24;'>🔒 ACCESO RESTRINGIDO</h2>", unsafe_allow_html=True)
        
        with st.container():
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                with st.form("login_form"):
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
