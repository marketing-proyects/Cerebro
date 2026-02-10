import streamlit as st
import os

def gestionar_login():
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        # Estilos para fondo blanco y botón rojo
        st.markdown("""
            <style>
            .stApp { background-color: #FFFFFF !important; }
            .logo-container { display: flex; justify-content: center; margin-bottom: 20px; }
            div.stButton > button {
                background-color: #ED1C24 !important;
                color: white !important;
                border: none !important;
                font-weight: bold !important;
                width: 100% !important;
            }
            /* Esto arregla el texto que no se lee */
            div.stButton > button p { color: white !important; }
            </style>
        """, unsafe_allow_html=True)
        
        # --- SOLUCIÓN LOGO ---
        st.markdown('<div class="logo-container">', unsafe_allow_html=True)
        
        # Intentamos cargar tu PNG local
        ruta_logo = "logo_wurth.png" 
        if os.path.exists(ruta_logo):
            st.image(ruta_logo, width=150)
        else:
            # Si el archivo no existe, mostramos el logo oficial por URL para evitar el "0"
            st.image("https://upload.wikimedia.org/wikipedia/commons/b/be/W%C3%BCrth_logo.svg", width=150)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("<h2 style='text-align: center; color: #ED1C24; margin-top:0;'>🔒 ACCESO AL SISTEMA</h2>", unsafe_allow_html=True)
        
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
