import streamlit as st
import os

def inyectar_animacion():
    # Eliminamos el IF para que la animación se inyecte siempre
    st.markdown("""
        <style>
        /* --- FONDO PERMANENTE --- */
        #animated-background {
            position: fixed; 
            top: 0; left: 0; width: 100%; height: 100%;
            z-index: 0; 
            background: #ffffff;
            pointer-events: none;
        }
        
        /* --- NEURONAS NEÓN --- */
        .neuron-node { 
            position: absolute; 
            border-radius: 50%; 
            background: #ffffff;
            opacity: 0.5;
            box-shadow: 0 0 12px 3px rgba(0, 212, 255, 0.7), 0 0 20px 8px rgba(0, 212, 255, 0.3);
            animation: floatNode 15s infinite ease-in-out;
        }
        
        .n1 { width: 15px; height: 15px; top: 15%; left: 10%; }
        .n2 { width: 22px; height: 22px; top: 75%; left: 85%; animation-duration: 20s; }
        .n3 { 
            width: 12px; height: 12px; top: 45%; left: 5%; 
            box-shadow: 0 0 12px 3px rgba(237, 28, 36, 0.6), 0 0 20px 8px rgba(237, 28, 36, 0.2);
            animation-duration: 12s;
        }
        .n4 { width: 18px; height: 18px; top: 80%; left: 35%; animation-duration: 25s; }

        /* --- SINAPSIS --- */
        .synapse {
            position: absolute;
            background: linear-gradient(90deg, rgba(0, 212, 255, 0) 0%, rgba(0, 212, 255, 0.2) 50%, rgba(0, 212, 255, 0) 100%);
            height: 2px;
            animation: pulseSynapse 10s infinite ease-in-out;
        }
        .s1 { width: 450px; top: 15%; left: 10%; transform: rotate(18deg); }
        .s2 { width: 550px; top: 75%; left: 85%; transform: rotate(-160deg); }

        @keyframes floatNode {
            0%, 100% { transform: translate(0, 0); }
            50% { transform: translate(20px, -20px); }
        }
        @keyframes pulseSynapse {
            0%, 100% { opacity: 0.1; }
            50% { opacity: 0.4; }
        }

        /* --- AJUSTE FORZADO DEL LOGO WÜRTH --- */
        /* Usamos CSS para forzar el margen independientemente de las columnas de Streamlit */
        .logo-container {
            position: absolute;
            top: 25px;    /* Espacio desde arriba */
            right: 25px;  /* Espacio desde la derecha */
            z-index: 99;  /* Por encima de todo */
            text-align: right;
        }
        .logo-container img {
            width: 160px !important;
            height: auto;
        }
        </style>
        
        <div id="animated-background">
            <div class="neuron-node n1"></div>
            <div class="neuron-node n2"></div>
            <div class="neuron-node n3"></div>
            <div class="neuron-node n4"></div>
            <div class="synapse s1"></div>
            <div class="synapse s2"></div>
        </div>
    """, unsafe_allow_html=True)

def gestionar_login():
    USUARIOS = {
        "admin": {"pass": "123", "permisos": ["Investigación de Mercado", "Fijación de Precios"]},
        "mkt_user": {"pass": "wurth2026", "permisos": ["Investigación de Mercado"]},
        "ventas_user": {"pass": "precios2026", "permisos": ["Fijación de Precios"]},
        "invitado": {"pass": "colega2026", "permisos": ["Investigación de Mercado", "Fijación de Precios"]}
    }

    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        st.markdown("<style>.stApp { background-color: white !important; }</style>", unsafe_allow_html=True)
        
        # Inyectamos la animación y el logo de forma absoluta
        inyectar_animacion()
        
        # Renderizado del Logo con posición absoluta vía CSS
        logo_path = os.path.join(os.getcwd(), "logo_wurth.png")
        if os.path.exists(logo_path):
            st.markdown(f'''
                <div class="logo-container">
                    <img src="data:image/png;base64,{st.image_to_base64(logo_path) if hasattr(st, "image_to_base64") else ""}" />
                </div>
            ''', unsafe_allow_html=True)
            # Como st.image es más fiable para cargar archivos locales:
            _, col_log = st.columns([5, 1])
            with col_log:
                st.markdown('<div style="padding-top: 25px; padding-right: 25px;">', unsafe_allow_html=True)
                st.image(logo_path, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown("<div class='logo-container'><h2 style='color: #ED1C24;'>WÜRTH</h2></div>", unsafe_allow_html=True)
        
        # Título de acceso
        st.markdown("<h3 style='text-align: center; color: #333; margin-top: 80px; margin-bottom: 30px;'>ACCESO AL SISTEMA</h3>", unsafe_allow_html=True)

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
