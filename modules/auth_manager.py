import streamlit as st
import os

def inyectar_animacion():
    # Eliminamos el check de session_state para que sea permanente
    st.markdown("""
        <style>
        #animated-background {
            position: fixed; 
            top: 0; left: 0; width: 100%; height: 100%;
            z-index: 0; 
            background: #ffffff;
            pointer-events: none;
        }
        
        .neuron-node { 
            position: absolute; 
            border-radius: 50%; 
            background: #ffffff;
            opacity: 0.3;
            box-shadow: 0 0 10px 2px rgba(0, 212, 255, 0.6), 0 0 20px 5px rgba(0, 212, 255, 0.2);
            animation: floatNode 15s infinite ease-in-out;
        }
        
        .n1 { width: 14px; height: 14px; top: 15%; left: 10%; }
        .n2 { width: 20px; height: 20px; top: 70%; left: 85%; animation-duration: 20s; }
        .n3 { 
            width: 12px; height: 12px; top: 40%; left: 5%; 
            box-shadow: 0 0 10px 2px rgba(237, 28, 36, 0.4), 0 0 20px 5px rgba(237, 28, 36, 0.1);
            animation-duration: 12s;
        }
        .n4 { width: 16px; height: 16px; top: 85%; left: 30%; animation-duration: 25s; }

        .synapse {
            position: absolute;
            background: linear-gradient(90deg, rgba(0, 212, 255, 0) 0%, rgba(0, 212, 255, 0.15) 50%, rgba(0, 212, 255, 0) 100%);
            height: 1px;
            transform-origin: 0 0;
            animation: pulseSynapse 10s infinite ease-in-out;
        }
        .s1 { width: 400px; top: 15%; left: 10%; transform: rotate(20deg); }
        .s2 { width: 500px; top: 70%; left: 85%; transform: rotate(-165deg); }

        @keyframes floatNode {
            0%, 100% { transform: translate(0, 0); }
            33% { transform: translate(10px, 15px); }
            66% { transform: translate(-5px, 5px); }
        }
        @keyframes pulseSynapse {
            0%, 100% { opacity: 0.05; }
            50% { opacity: 0.2; }
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
    # Diccionario actualizado con el usuario de prueba para colegas
    USUARIOS = {
        "admin": {"pass": "123", "permisos": ["Investigación de Mercado", "Fijación de Precios"]},
        "mkt_user": {"pass": "wurth2026", "permisos": ["Investigación de Mercado"]},
        "ventas_user": {"pass": "precios2026", "permisos": ["Fijación de Precios"]},
        "invitado": {"pass": "colega2026", "permisos": ["Investigación de Mercado"]} # Usuario de prueba
    }

    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        st.markdown("<style>.stApp { background-color: white !important; }</style>", unsafe_allow_html=True)
        
        inyectar_animacion()
        
        # --- AJUSTE DE LOGO: Margen superior y lateral ---
        col_vacia, col_logo = st.columns([5, 1])
        with col_logo:
            # Agregamos un div contenedor con padding para alejarlo de los bordes
            st.markdown('<div style="padding: 20px 20px 0 0; text-align: right;">', unsafe_allow_html=True)
            logo_path = os.path.join(os.getcwd(), "logo_wurth.png")
            if os.path.exists(logo_path):
                st.image(logo_path, use_container_width=True)
            else:
                st.markdown("<h2 style='color: #ED1C24; margin: 0;'>WÜRTH</h2>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("<h3 style='text-align: center; color: #333; margin-top: 10px; margin-bottom: 25px;'>ACCESO CEREBRO</h3>", unsafe_allow_html=True)

        with st.container():
            _, center, _ = st.columns([1, 2, 1])
            with center:
                with st.form("login_form_final"):
                    user = st.text_input("Usuario")
                    password = st.text_input("Contraseña", type="password")
                    submit = st.form_submit_button("INGRESAR AL SISTEMA", use_container_width=True)
                    
                    if submit:
                        if user in USUARIOS and USUARIOS[user]["pass"] == password:
                            st.session_state["autenticado"] = True
                            st.session_state["username"] = user
                            st.session_state["permisos"] = USUARIOS[user]["permisos"]
                            st.rerun()
                        else:
                            st.error("Credenciales incorrectas")
        return False
    return True
