import streamlit as st
import os

def inyectar_animacion():
    # Animación solo para la primera vez en la sesión
    if 'animacion_mostrada' not in st.session_state:
        st.markdown("""
            <style>
            /* Contenedor principal de la animación */
            #animated-background {
                position: fixed; 
                top: 0; left: 0; width: 100%; height: 100%;
                z-index: 0; 
                background: #ffffff;
                /* Desaparece a los 5 segundos exactos */
                animation: fadeOutBackground 1.5s ease-in-out 3.5s forwards;
                pointer-events: none; /* Evita que bloquee los clics en el formulario */
            }
            
            /* Animación de desaparición */
            @keyframes fadeOutBackground { 
                0% { opacity: 1; } 
                100% { opacity: 0; visibility: hidden; z-index: -10; } 
            }
            
            /* Movimiento flotante sutil */
            @keyframes float { 
                0% { transform: translateY(0px) translateX(0px); } 
                50% { transform: translateY(-15px) translateX(10px); } 
                100% { transform: translateY(0px) translateX(0px); } 
            }
            
            /* Puntos (Nodos) */
            .particle { position: absolute; border-radius: 50%; }
            .p1 { width: 8px; height: 8px; background: rgba(150, 150, 150, 0.3); top: 25%; left: 25%; animation: float 6s infinite; }
            .p2 { width: 12px; height: 12px; background: rgba(150, 150, 150, 0.2); top: 65%; left: 75%; animation: float 8s infinite; }
            .p3 { width: 6px; height: 6px; background: rgba(237, 28, 36, 0.4); top: 45%; left: 15%; animation: float 5s infinite; } /* Toque rojo Würth */
            .p4 { width: 10px; height: 10px; background: rgba(150, 150, 150, 0.3); top: 75%; left: 35%; animation: float 7s infinite; }
            
            /* Líneas conectoras */
            .connecting-line { position: absolute; background: rgba(150, 150, 150, 0.15); height: 1px; transform-origin: 0 0; }
            .l1 { width: 250px; top: 25%; left: 25%; transform: rotate(15deg); animation: pulseLine 4s infinite; }
            .l2 { width: 350px; top: 65%; left: 75%; transform: rotate(-20deg); animation: pulseLine 5s infinite;}
            
            @keyframes pulseLine { 0%, 100% { opacity: 0.1; } 50% { opacity: 0.5; } }
            </style>
            
            <div id="animated-background">
                <div class="particle p1"></div>
                <div class="particle p2"></div>
                <div class="particle p3"></div>
                <div class="particle p4"></div>
                <div class="connecting-line l1"></div>
                <div class="connecting-line l2"></div>
            </div>
        """, unsafe_allow_html=True)
        
        # Guardamos en memoria que ya se mostró
        st.session_state['animacion_mostrada'] = True

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
        
        # 1. Llamado a la animación de fondo
        inyectar_animacion()
        
        # 2. Logo a la derecha
        # Usamos una columna muy ancha vacía y una pequeña a la derecha para el logo
        col_vacia, col_logo = st.columns([5, 1])
        with col_logo:
            # Ruta absoluta para evitar errores en Streamlit Cloud
            logo_path = os.path.join(os.getcwd(), "logo_wurth.png")
            if os.path.exists(logo_path):
                st.image(logo_path, use_container_width=True)
            else:
                # Si no encuentra la imagen, pone el texto alineado a la derecha
                st.markdown("<h2 style='color: #ED1C24; text-align: right; margin-top: 0;'>WÜRTH</h2>", unsafe_allow_html=True)
        
        # 3. Título centrado (independiente del logo)
        st.markdown("<h3 style='text-align: center; color: #333; margin-top: -30px; margin-bottom: 20px;'>ACCESO A INVESTIGADOR AL SISTEMA</h3>", unsafe_allow_html=True)

        # 4. Formulario de Login original
        with st.container():
            _, center, _ = st.columns([1, 2, 1])
            with center:
                with st.form("login_form_final"):
                    user = st.text_input("Usuario")
                    password = st.text_input("Contraseña", type="password
