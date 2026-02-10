import streamlit as st

def gestionar_login():
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        # CSS para centrar el logo y arreglar el botón
        st.markdown("""
            <style>
            .logo-container {
                display: flex;
                justify-content: center;
                margin-bottom: 20px;
            }
            /* Forzar texto blanco en el botón */
            div.stButton > button p {
                color: white !important;
            }
            </style>
        """, unsafe_allow_html=True)
        
        # --- EL LOGO USANDO LA URL ---
        st.markdown('<div class="logo-container">', unsafe_allow_html=True)
        st.image("https://upload.wikimedia.org/wikipedia/commons/b/be/W%C3%BCrth_logo.svg", width=120)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Resto del formulario...
        with st.form("login_form"):
            user = st.text_input("Usuario")
            password = st.text_input("Contraseña", type="password")
            if st.form_submit_button("INGRESAR AL SISTEMA"):
                if user == "admin" and password == "123":
                    st.session_state["autenticado"] = True
                    st.session_state["username"] = user
                    st.rerun()
        return False
    return True
