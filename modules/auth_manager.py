import streamlit as st

def gestionar_login():
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        # CSS para forzar el texto blanco y el fondo rojo sólido
        st.markdown("""
            <style>
            div.stButton > button {
                background-color: #ED1C24 !important;
                color: white !important;
                border: 2px solid #ED1C24 !important;
                font-weight: bold !important;
                width: 100% !important;
                height: 3em !important;
            }
            div.stButton > button:hover {
                background-color: #B3151A !important;
                color: white !important;
                border-color: #B3151A !important;
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
                    # El botón ahora heredará el estilo del CSS de arriba
                    if st.form_submit_button("INGRESAR AL SISTEMA"):
                        if user == "admin" and password == "123":
                            st.session_state["autenticado"] = True
                            st.session_state["username"] = user
                            st.rerun()
                        else:
                            st.error("Credenciales incorrectas")
        return False
    return True
