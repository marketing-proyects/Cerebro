import streamlit as st

def gestionar_login():
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        # Estilos para centrar el logo sobre el formulario
        st.markdown("""
            <style>
            .stApp { background-color: #FFFFFF !important; }
            .login-header {
                display: flex;
                flex-direction: column;
                align-items: center;
                margin-bottom: 20px;
            }
            div.stButton > button {
                background-color: #ED1C24 !important;
                color: white !important;
                font-weight: bold !important;
                width: 100% !important;
                height: 3em !important;
            }
            div.stButton > button p { color: white !important; }
            </style>
        """, unsafe_allow_html=True)

        # Contenedor del Logo y Título encima del cuadro
        st.markdown('<div class="login-header">', unsafe_allow_html=True)
        st.image("https://upload.wikimedia.org/wikipedia/commons/b/be/W%C3%BCrth_logo.svg", width=180)
        st.markdown("<h2 style='color: #ED1C24; margin-top: 15px;'>ACCESO CEREBRO</h2>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        with st.container():
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                with st.form(key="login_central"):
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
