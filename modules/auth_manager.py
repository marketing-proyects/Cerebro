import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

def gestionar_login():
    with open('config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)

    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days']
    )

    # El formulario se renderiza aquí
    authenticator.login(location='main')
