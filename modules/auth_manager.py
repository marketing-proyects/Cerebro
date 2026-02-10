import streamlit as st

def gestionar_login():
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        # CSS para fondo blanco y botones rojos legibles
        st.markdown("""
            <style>
            /* Fondo blanco para el área de login */
            .stApp { background-color: #FFFFFF !important; color: #000000 !important; }
            
            /* Logo centrado */
            .logo-container { display: flex; justify-content: center; margin-bottom: 20px; }
            
            /* Botón Rojo con texto Blanco Garantizado */
            div.stButton > button {
                background-color: #ED1C24 !important;
                color: white !important;
                border: none !important;
                font-weight: bold !important;
                width: 100% !important;
                height: 3em !important;
            }
            div.stButton > button p { color: white !important; }
            
            /* Inputs con borde gris suave */
            .stTextInput > div > div > input { border-color: #CCCCCC !important; }
            </style>
        """, unsafe_allow_html=True)
        
        # Logo de Würth
        st.markdown('<div class="logo-container">', unsafe_allow_html=True)
        st.image("https://upload.wikimedia.org/wikipedia/commons/b/be/W%C3%BCrth_logo.svg", width=150)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("<h2 style='text-align: center; color: #ED1C24;'>🔒 ACCESO AL SISTEMA</h2>", unsafe_allow_html=True)
        
        with st.container():
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                with st.form("login_form"):
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
