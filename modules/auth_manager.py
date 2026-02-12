import streamlit as st
import os

def gestionar_login():
    # Diccionario de usuarios y permisos
    USUARIOS = {
        "admin": {"pass": "123", "permisos": ["Investigación de Mercado", "Fijación de Precios"]},
        "mkt_user": {"pass": "wurth2026", "permisos": ["Investigación de Mercado"]},
        "ventas_user": {"pass": "precios2026", "permisos": ["Fijación de Precios"]}
    }

    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        st.markdown("<style>.stApp { background-color: white !important; }</style>", unsafe_allow_html=True)
        
        # Logo Würth - Centrado
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            # Ruta absoluta para evitar errores en Streamlit Cloud
            logo_path = os.path.join(os.getcwd(), "logo_wurth.png")
            if os.path.exists(logo_path):
                st.image(logo_path, width=220)
            else:
                st.markdown("<h1 style='color: #ED1C24; text-align: center;'>WÜRTH</h1>", unsafe_allow_html=True)
            
            st.markdown("<h3 style='text-align: center; color: #333;'>ACCESO CEREBRO</h3>", unsafe_allow_html=True)

        with st.container():
            _, center, _ = st.columns([1, 2, 1])
            with center:
                with st.form("login_form_final"):
                    user = st.text_input("Usuario")
                    password = st.text_input("Contraseña", type="password")
                    if st.form_submit_button("INGRESAR AL SISTEMA"):
                        if user in USUARIOS and USUARIOS[user]["pass"] == password:
                            st.session_state["autenticado"] = True
                            st.session_state["username"] = user
                            st.session_state["permisos"] = USUARIOS[user]["permisos"]
                            st.rerun()
                        else:
                            st.error("Credenciales incorrectas")
        return False
    return True
