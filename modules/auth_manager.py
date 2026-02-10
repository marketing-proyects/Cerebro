import streamlit as st

def gestionar_login():
    # Inicializamos el estado de autenticación
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        # Estética de la pantalla de login
        st.markdown("<h2 style='text-align: center; color: #00FBFF;'>🔒 ACCESO RESTRINGIDO</h2>", unsafe_allow_html=True)
        
        with st.container():
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                with st.form("login_form"):
                    user = st.text_input("Usuario")
                    password = st.text_input("Contraseña", type="password")
                    btn_login = st.form_submit_button("INGRESAR AL SISTEMA")

                    if btn_login:
                        # Validación directa (puedes cambiar '123' por st.secrets["password"] luego)
                        if user == "admin" and password == "123":
                            st.session_state["autenticado"] = True
                            st.session_state["username"] = user
                            st.rerun()
                        else:
                            st.error("Credenciales incorrectas. Verifique el acceso.")
        return False
    
    return True
