import streamlit as st
import hashlib
import json
import os
from datetime import datetime

def hash_password(password):
    """Hash le mot de passe avec SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    """Charge les utilisateurs depuis le fichier JSON"""
    if os.path.exists('data/users.json'):
        with open('data/users.json', 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    """Sauvegarde les utilisateurs dans le fichier JSON"""
    if not os.path.exists('data'):
        os.makedirs('data')
    with open('data/users.json', 'w') as f:
        json.dump(users, f)

# Configuration de la page
st.set_page_config(
    page_title="Connexion - Lexaflow",
    page_icon="🔐",
    layout="centered"
)

# Titre et description
st.title("🔐 Connexion")
st.markdown("""
    ### Bienvenue sur Lexaflow
    Connectez-vous pour accéder à votre espace de génération de descriptions produits.
""")

# Initialisation de la session state pour l'authentification
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# Formulaire de connexion
with st.form("login_form"):
    username = st.text_input("Nom d'utilisateur")
    password = st.text_input("Mot de passe", type="password")
    submitted = st.form_submit_button("Se connecter")
    
    if submitted:
        users = load_users()
        if username in users and users[username]['password'] == hash_password(password):
            st.session_state.authenticated = True
            st.session_state.username = username
            st.success("Connexion réussie!")
            st.switch_page("app.py")
        else:
            st.error("Nom d'utilisateur ou mot de passe incorrect")

# Option pour créer un nouveau compte
st.markdown("---")
st.markdown("Vous n'avez pas encore de compte ?")
if st.button("Créer un nouveau compte"):
    st.switch_page("pages/register.py") 