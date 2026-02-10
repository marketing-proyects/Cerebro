import streamlit as st

def gestionar_login():
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        st.markdown("""
            <style>
            .stApp { background-color: #FFFFFF !important; }
            div.stButton > button {
                background-color: #ED1C24 !important;
                color: white !important;
                border: none !important;
                font-weight: bold !important;
                width: 100% !important;
                height: 3em !important;
            }
            div.stButton > button p { color: white !important; }
            </style>
        """, unsafe_allow_html=True)

        st.markdown("<h2 style='text-align: center; color: #ED1C24;'>🔒 ACCESO CEREBRO</h2>", unsafe_allow_html=True)
        
        with st.container():
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                with st.form(key="login_final"):
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
