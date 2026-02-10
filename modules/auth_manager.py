import streamlit as st

def gestionar_login():
    # Inicializamos el estado para evitar que aparezca el "0"
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        # CSS Ultra-específico para el botón y el logo
        st.markdown("""
            <style>
            /* FORZAR TEXTO BLANCO EN EL BOTÓN */
            div.stButton > button {
                background-color: #ED1C24 !important;
                color: white !important; /* Blanco sólido */
                border: 2px solid #ED1C24 !important;
                font-weight: bold !important;
                width: 100% !important;
                height: 3.5em !important;
            }
            /* Asegurar que el texto dentro del párrafo del botón sea blanco */
            div.stButton > button p {
                color: white !important;
            }
            </style>
        """, unsafe_allow_html=True)
        
        # Logo de Würth centrado antes del acceso
        st.columns([1, 1, 1])[1].image("https://upload.wikimedia.org/wikipedia/commons/b/be/W%C3%BCrth_logo.svg", width=120)
        
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
