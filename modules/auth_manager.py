import streamlit as st

def gestionar_login():
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        # CSS Ultra-específico para forzar texto blanco y centrar logo
        st.markdown("""
            <style>
            /* Contenedor del Logo en Login */
            .login-logo {
                display: flex;
                justify-content: center;
                margin-bottom: 20px;
            }
            
            /* FORZAR TEXTO BLANCO EN EL BOTÓN */
            div.stButton > button {
                background-color: #ED1C24 !important;
                color: #FFFFFF !important; /* Blanco puro */
                border: 2px solid #ED1C24 !important;
                font-weight: bold !important;
                width: 100% !important;
                height: 3.5em !important;
                opacity: 1 !important;
            }
            
            /* Asegurar que el texto siga blanco al pasar el mouse */
            div.stButton > button:hover, div.stButton > button:active, div.stButton > button:focus {
                color: #FFFFFF !important;
                background-color: #B3151A !important;
                border-color: #B3151A !important;
            }

            /* Fix para el texto dentro del formulario de Streamlit */
            div.stButton > button p {
                color: white !important;
            }
            </style>
        """, unsafe_allow_html=True)
        
        # Logo de Würth antes del Login
        st.markdown('<div class="login-logo">', unsafe_allow_html=True)
        st.image("https://upload.wikimedia.org/wikipedia/commons/b/be/W%C3%BCrth_logo.svg", width=120)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("<h2 style='text-align: center; color: #ED1C24; margin-top: 0;'>🔒 ACCESO RESTRINGIDO</h2>", unsafe_allow_html=True)
        
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
