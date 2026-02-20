import streamlit as st
import os
import base64

def get_image_base64(path):
    """Convierte el logo JPG a base64 para inyectarlo sin depender de URLs externas."""
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

def inyectar_animacion():
    # 1. Carga del logo JPG local
    logo_path = os.path.join(os.getcwd(), "logo_wurth.jpg")
    img_base64 = get_image_base64(logo_path)
    
    # Preparación del estilo (si no hay imagen, ponemos texto por seguridad)
    logo_content = f"url('data:image/jpeg;base64,{img_base64}')" if img_base64 else "none"

    st.markdown(f"""
        <style>
        /* --- ESTADO GENERAL --- */
        .stApp {{ background: white !important; }}
        
        #cerebro-bg {{
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            z-index: 0;
            background: #ffffff;
            pointer-events: none;
        }}

        /* --- LOGO WÜRTH --- */
        #logo-superior {{
            position: fixed;
            top: 65px;
            right: 40px; 
            width: 170px;
            height: 50px;
            z-index: 9999;
            background-image: {logo_content};
            background-size: contain;
            background-repeat: no-repeat;
            background-position: right;
        }}

        /* --- NEURONAS ANIMADAS --- */
        .neuron {{
            position: absolute;
            border-radius: 50%;
            background: #ffffff;
            opacity: 0.6;
            animation: moveNeuron 20s infinite linear;
        }}

        .n1 {{ width: 15px; height: 15px; top: 20%; left: 15%; box-shadow: 0 0 15px 5px rgba(0, 212, 255, 0.7); }}
        .n2 {{ width: 12px; height: 12px; top: 50%; left: 80%; box-shadow: 0 0 15px 5px rgba(237, 28, 36, 0.6); animation-duration: 25s; }}
        .n3 {{ width: 20px; height: 20px; top: 80%; left: 30%; box-shadow: 0 0 20px 8px rgba(0, 212, 255, 0.4); animation-duration: 30s; }}

        @keyframes moveNeuron {{
            0% {{ transform: translate(0, 0); }}
            33% {{ transform: translate(30px, 40px); }}
            66% {{ transform: translate(-20px, 20px); }}
            100% {{ transform: translate(0, 0); }}
        }}
        </style>

        <div id="cerebro-bg">
            <div id="logo-superior"></div>
            <div class="neuron n1"></div>
            <div class="neuron n2"></div>
            <div class="neuron n3"></div>
        </div>
    """, unsafe_allow_html=True)

def gestionar_login():
    # Diccionario actualizado con el nuevo nombre del módulo de Liquidación
    USUARIOS = {
        "admin": {
            "pass": "123", 
            "permisos": ["Investigación de Mercado", "Fijación de Precios", "Liquidación (Prox. vencimientos)"]
        },
        "usuario_marketing": {
            "pass": "marketing2026", 
            "permisos": ["Investigación de Mercado"]
        },
        "usuario_director": {
            "pass": "director2026", 
            "permisos": ["Fijación de Precios"]
        },
        "usuario_invitado": {
            "pass": "invitado2026", 
            "permisos": ["Investigación de Mercado", "Fijación de Precios", "Liquidación (Prox. vencimientos)"]
        }
    }

    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        inyectar_animacion()
        
        st.markdown("<h3 style='text-align: center; color: #333; margin-top: 160px; margin-bottom: 30px;'>ACCESO CEREBRO</h3>", unsafe_allow_html=True)

        with st.container():
            _, center, _ = st.columns([1, 2, 1])
            with center:
                with st.form("login_form_final"):
                    user = st.text_input("Usuario")
                    password = st.text_input("Contraseña", type="password")
                    if st.form_submit_button("INGRESAR AL SISTEMA", use_container_width=True):
                        if user in USUARIOS and USUARIOS[user]["pass"] == password:
                            st.session_state["autenticado"] = True
                            st.session_state["username"] = user
                            st.session_state["permisos"] = USUARIOS[user]["permisos"]
                            st.rerun()
                        else:
                            st.error("Credenciales incorrectas")
        return False
    return True
