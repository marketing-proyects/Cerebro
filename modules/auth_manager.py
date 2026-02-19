import streamlit as st
import os

def inyectar_animacion():
    # Inyectamos el fondo, las neuronas y el logo vía CSS puro para máximo control
    st.markdown("""
        <style>
        /* --- FONDO BLANCO PERMANENTE --- */
        #cerebro-bg {
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            z-index: -1;
            background: #ffffff;
            pointer-events: none;
        }

        /* --- LOGO WÜRTH (JPG) POSICIONADO CON PRECISIÓN --- */
        #logo-superior {
            position: fixed;
            top: 30px;    /* Margen desde el techo */
            right: 30px;  /* Margen desde la derecha */
            width: 180px;
            height: auto;
            z-index: 100;
            content: url("https://raw.githubusercontent.com/marketing-proyects/Cerebro/main/logo_wurth.jpg");
        }

        /* --- NEURONAS NEÓN (ANIMACIÓN REFORZADA) --- */
        .neuron {
            position: absolute;
            border-radius: 50%;
            background: #ffffff;
            opacity: 0.5;
            animation: moveNeuron 20s infinite linear;
        }

        /* Nodo Cian con Resplandor */
        .n1 { 
            width: 15px; height: 15px; top: 20%; left: 15%; 
            box-shadow: 0 0 15px 5px rgba(0, 212, 255, 0.7); 
        }
        /* Nodo Rojo (Würth Style) con Resplandor */
        .n2 { 
            width: 12px; height: 12px; top: 50%; left: 80%; 
            box-shadow: 0 0 15px 5px rgba(237, 28, 36, 0.6);
            animation-duration: 25s;
        }
        /* Nodo Cian Grande */
        .n3 { 
            width: 20px; height: 20px; top: 80%; left: 30%; 
            box-shadow: 0 0 20px 8px rgba(0, 212, 255, 0.4);
            animation-duration: 30s;
        }

        /* --- KEYFRAMES PARA MOVIMIENTO --- */
        @keyframes moveNeuron {
            0% { transform: translate(0, 0); }
            33% { transform: translate(30px, 50px); }
            66% { transform: translate(-20px, 20px); }
            100% { transform: translate(0, 0); }
        }

        /* Forzar que el App de Streamlit sea transparente para ver el fondo */
        .stApp { background: transparent !important; }
        </style>

        <div id="cerebro-bg">
            <div class="neuron n1"></div>
            <div class="neuron n2"></div>
            <div class="neuron n3"></div>
        </div>
        <div id="logo-superior"></div>
    """, unsafe_allow_html=True)

def gestionar_login():
    USUARIOS = {
        "admin": {"pass": "123", "permisos": ["Investigación de Mercado", "Fijación de Precios"]},
        "mkt_user": {"pass": "wurth2026", "permisos": ["Investigación de Mercado"]},
        "ventas_user": {"pass": "precios2026", "permisos": ["Fijación de Precios"]},
        "prueba": {"pass": "123", "permisos": ["Investigación de Mercado"]}
    }

    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        # Inyectamos toda la visual (Fondo, Animación y Logo)
        inyectar_animacion()
        
        # Título centrado (Se baja margen para que no choque con el logo)
        st.markdown("<h3 style='text-align: center; color: #333; margin-top: 120px; margin-bottom: 30px;'>ACCESO CEREBRO</h3>", unsafe_allow_html=True)

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
