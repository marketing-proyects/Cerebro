import streamlit as st
import os

def inyectar_animacion():
    if 'animacion_mostrada' not in st.session_state:
        st.markdown("""
            <style>
            #animated-background {
                position: fixed; 
                top: 0; left: 0; width: 100%; height: 100%;
                z-index: 0; 
                background: #ffffff;
                /* Eliminamos la animación de desaparición */
                pointer-events: none;
            }
            
            /* --- Neuronas Neón con movimiento perpetuo --- */
            .neuron-node { 
                position: absolute; 
                border-radius: 50%; 
                background: #ffffff;
                /* Bajamos la opacidad para que no distraiga al trabajar */
                opacity: 0.4;
                box-shadow: 0 0 10px 2px rgba(0, 212, 255, 0.6), 0 0 20px 5px rgba(0, 212, 255, 0.2);
                animation: floatNode 12s infinite ease-in-out; /* Más lento */
            }
            
            .n1 { width: 14px; height: 14px; top: 15%; left: 10%; }
            .n2 { width: 20px; height: 20px; top: 70%; left: 85%; animation-duration: 15s; }
            .n3 { 
                width: 12px; height: 12px; top: 40%; left: 5%; 
                box-shadow: 0 0 10px 2px rgba(237, 28, 36, 0.5), 0 0 20px 5px rgba(237, 28, 36, 0.2);
                animation-duration: 10s;
            }
            .n4 { width: 16px; height: 16px; top: 85%; left: 30%; animation-duration: 18s; }

            /* --- Haces de energía (Sinapsis) --- */
            .synapse {
                position: absolute;
                background: linear-gradient(90deg, rgba(0, 212, 255, 0) 0%, rgba(0, 212, 255, 0.2) 50%, rgba(0, 212, 255, 0) 100%);
                height: 1px;
                transform-origin: 0 0;
                animation: pulseSynapse 8s infinite ease-in-out;
            }
            .s1 { width: 400px; top: 15%; left: 10%; transform: rotate(20deg); }
            .s2 { width: 500px; top: 70%; left: 85%; transform: rotate(-165deg); }

            @keyframes floatNode {
                0%, 100% { transform: translate(0, 0); }
                33% { transform: translate(15px, 20px); }
                66% { transform: translate(-10px, 10px); }
            }
            @keyframes pulseSynapse {
                0%, 100% { opacity: 0.1; }
                50% { opacity: 0.4; }
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
        # Nota: quitamos el st.session_state para que se mantenga siempre visible
