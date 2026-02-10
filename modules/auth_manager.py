import streamlit as st

def gestionar_login():
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        # Estilos para centrar el logo y arreglar el botón
        st.markdown("""
            <style>
            .stApp { background-color: #FFFFFF !important; }
            .login-box {
                display: flex;
                flex-direction: column;
                align-items: center;
                margin-top: 20px;
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

        # Logo centrado arriba del formulario
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.image("https://upload.wikimedia.org/wikipedia/commons/b/be/W%C3%BCrth_logo.svg", width=180)
        st.markdown("<h2 style='color: #ED1C24; margin-top: 15px;'>ACCESO AL SISTEMA</h2>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        with st.container():
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                with st.form(key="login_central_rigid"):
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
    return True
