import streamlit as st
import os

def inyectar_animacion():
    # Solo mostrar la animación si es la primera vez en la sesión
    if 'animacion_mostrada' not in st.session_state:
        st.markdown("""
            <style>
            /* --- Contenedor principal --- */
            #animated-background {
                position: fixed; 
                top: 0; left: 0; width: 100%; height: 100%;
                z-index: 0; 
                background: #ffffff;
                animation: fadeOutBackground 1.5s ease-in-out 3.5s forwards;
                pointer-events: none;
            }
            
            @keyframes fadeOutBackground { 
                0% { opacity: 1; } 
                100% { opacity: 0; visibility: hidden; z-index: -10; } 
            }
            
            /* --- Estilo Neón para Neuronas --- */
            .neuron-node { 
                position: absolute; 
                border-radius: 50%; 
                background: #ffffff;
                /* Efecto de resplandor Neón Cian */
                box-shadow: 0 0 10px 2px rgba(0, 212, 255, 0.7), 0 0 20px 5px rgba(0, 212, 255, 0.3);
                animation: floatNode 6s infinite ease-in-out;
            }
            
            .n1 { width: 14px; height: 14px; top: 20%; left: 20%; }
            .n2 { width: 18px; height: 18px; top: 60%; left: 80%; animation-delay: 1s; }
            /* Nodo Neón Rojo (Acento Würth) */
            .n3 { 
                width: 12px; height: 12px; top: 40%; left: 10%; 
                box-shadow: 0 0 10px 2px rgba(237, 28, 36, 0.7), 0 0 20px 5px rgba(237, 28, 36, 0.3);
                animation-delay: 2s;
            }
            .n4 { width: 16px; height: 16px; top: 80%; left: 40%; animation-delay: 0.5s; }

            /* --- Conexiones Eléctricas (Sinapsis) --- */
            .synapse {
                position: absolute;
                background: linear-gradient(90deg, rgba(0, 212, 255, 0) 0%, rgba(0, 212, 255, 0.4) 50%, rgba(0, 212, 255, 0) 100%);
                height: 2px;
                transform-origin: 0 0;
                animation: pulseSynapse 4s infinite ease-in-out;
            }
            .s1 { width: 300px; top: 20%; left: 20%; transform: rotate(15deg); }
            .s2 { width: 400px; top: 60%; left: 80%; transform: rotate(-160deg); }

            @keyframes floatNode {
                0%, 100% { transform: translate(0, 0); }
                50% { transform: translate(10px, -15px); }
            }
            @keyframes pulseSynapse {
                0%, 100% { opacity: 0.2; transform: scaleX(1); }
                50% { opacity: 0.8; transform: scaleX(1.05); }
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
        st.session_state['animacion_mostrada'] = True

def gestionar_login():
    USUARIOS = {
        "admin": {"pass": "123", "permisos": ["Investigación de Mercado", "Fijación de Precios"]},
        "mkt_user": {"pass": "wurth2026", "permisos": ["Investigación de Mercado"]},
        "usuario_prueba": {"pass": "usuario_123", "permisos": ["Investigación de Mercado", "Fijación de Precios"]}
    }

    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        st.markdown("<style>.stApp { background-color: white !important; }</style>", unsafe_allow_html=True)
        
        inyectar_animacion()
        
        # --- AJUSTE DE LOGO CON MARGEN ---
        # Usamos padding para que no toque los bordes (margen de seguridad)
        col_vacia, col_logo = st.columns([5, 1])
        with col_logo:
            st.markdown('<div style="padding: 10px; text-align: right;">', unsafe_allow_html=True)
            logo_path = os.path.join(os.getcwd(), "logo_wurth.png")
            if os.path.exists(logo_path):
                st.image(logo_path, use_container_width=True)
            else:
                st.markdown("<h2 style='color: #ED1C24; margin: 0;'>WÜRTH</h2>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("<h3 style='text-align: center; color: #333; margin-top: -20px; margin-bottom: 20px;'>ACCESO CEREBRO</h3>", unsafe_allow_html=True)

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
