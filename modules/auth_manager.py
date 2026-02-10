import streamlit as st

def gestionar_login():
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        # CSS para forzar el logo arriba y el texto blanco en el botón
        st.markdown("""
            <style>
            /* Centrar logo */
            .logo-container { display: flex; justify-content: center; margin-bottom: -20px; }
            
            /* FORZAR TEXTO BLANCO */
            div.stButton > button {
                background-color: #ED1C24 !important;
                color: white !important;
                border: 2px solid #ED1C24 !important;
                font-weight: bold !important;
                width: 100% !important;
            }
            /* Este es el truco para el texto invisible */
            div.stButton > button p {
                color: white !important;
            }
            </style>
        """, unsafe_allow_html=True)
        
        # Logo pre login
        st.markdown('<div class="logo-container">', unsafe_allow_html=True)
        st.image("logo_wurth.png", width=120)
        st.markdown('</div>', unsafe_allow_html=True)
        
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
