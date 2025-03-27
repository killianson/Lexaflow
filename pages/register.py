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
    page_title="Inscription - Lexaflow",
    page_icon="📝",
    layout="centered"
)

# Titre et description
st.title("📝 Création de compte")
st.markdown("""
    ### Rejoignez Lexaflow
    Créez votre compte pour accéder à notre générateur de descriptions produits.
""")

# Formulaire d'inscription
with st.form("register_form"):
    new_username = st.text_input("Choisissez un nom d'utilisateur")
    new_password = st.text_input("Choisissez un mot de passe", type="password")
    confirm_password = st.text_input("Confirmez le mot de passe", type="password")
    submitted = st.form_submit_button("Créer le compte")
    
    if submitted:
        if new_password != confirm_password:
            st.error("Les mots de passe ne correspondent pas")
        else:
            users = load_users()
            if new_username in users:
                st.error("Ce nom d'utilisateur existe déjà")
            else:
                users[new_username] = {
                    'password': hash_password(new_password),
                    'created_at': str(datetime.now())
                }
                save_users(users)
                st.success("Compte créé avec succès!")
                st.switch_page("pages/login.py")

# Option pour retourner à la connexion
st.markdown("---")
st.markdown("Déjà un compte ?")
if st.button("Retour à la connexion"):
    st.switch_page("pages/login.py") 