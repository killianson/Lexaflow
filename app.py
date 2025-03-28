import streamlit as st
import openai
from dotenv import load_dotenv
import os
import pandas as pd
from datetime import datetime
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

daily_limit = 10

# Configuration de la page (doit être la première commande Streamlit)
st.set_page_config(
    page_title="Lexaflow - Générateur de Descriptions Produits",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def check_daily_limit(email):
    try:
        # Créer le dossier data s'il n'existe pas
        if not os.path.exists('data'):
            os.makedirs('data')
        
        # Chemin du fichier de compteur
        counter_file = 'data/daily_counter.json'
        
        # Charger ou initialiser le compteur
        if os.path.exists(counter_file):
            with open(counter_file, 'r') as f:
                counters = json.load(f)
        else:
            counters = {}
        
        # Vérifier si l'utilisateur a un compteur pour aujourd'hui
        today = datetime.now().strftime('%Y-%m-%d')
        if email not in counters:
            counters[email] = {'date': today, 'count': 0}
        
        # Réinitialiser le compteur si c'est un nouveau jour
        if counters[email]['date'] != today:
            counters[email] = {'date': today, 'count': 0}
        
        # Vérifier la limite
        if counters[email]['count'] >= daily_limit:
            return False
        
        # Incrémenter le compteur
        counters[email]['count'] += 1
        
        # Sauvegarder le compteur
        with open(counter_file, 'w') as f:
            json.dump(counters, f)
        
        return True
    except Exception as e:
        st.error(f"Erreur lors de la vérification de la limite : {str(e)}")
        return False

# Vérification de l'authentification
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.warning("Veuillez vous connecter pour accéder à l'application.")
    st.switch_page("pages/login.py")

# Configuration de la clé API OpenAI (gestion local/production)
try:
    # Essayer d'abord les secrets Streamlit (production)
    openai.api_key = st.secrets["OPENAI_API_KEY"]
except:
    # Si échec, utiliser le fichier .env (développement local)
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")

# Ajout du JavaScript personnalisé pour la copie
st.markdown("""
    <script>
    function copyToClipboard(text) {
        navigator.clipboard.writeText(text).then(function() {
            console.log('Texte copié avec succès');
        }).catch(function(err) {
            console.error('Erreur lors de la copie: ', err);
        });
    }
    </script>
""", unsafe_allow_html=True)

# Titre et description
st.title("✨ Lexaflow")
st.markdown("""
    ### Générateur intelligent de descriptions produits
    Créez des descriptions de produits optimisées SEO en quelques clics.
""")

# Bouton de déconnexion
if st.button("Se déconnecter"):
    st.session_state.authenticated = False
    st.switch_page("pages/login.py")

def log_feedback(product_name, description, is_satisfied, feedback_text):
    try:
        # Configuration de l'accès à Google Sheets
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds_dict = json.loads(st.secrets["GCP_CREDENTIALS"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        sheet = client.open('Lexaflow Feedback').sheet1
        
        # Préparer la nouvelle ligne de feedback
        new_row = [
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            product_name,
            description,
            str(is_satisfied),
            feedback_text
        ]
        
        # Ajouter le feedback
        sheet.append_row(new_row)
        return True
        
    except Exception as e:
        st.error(f"Erreur lors de l'enregistrement du feedback : {str(e)}")
        return False

def generate_product_description(product_name, category, audience, tone, features, keywords):
    # Construction du prompt
    prompt = f"""En tant qu'expert en rédaction e-commerce, créez une description de produit optimisée SEO pour le produit suivant :

Nom du produit : {product_name}
Catégorie : {category}
Public cible : {', '.join(audience)}
Ton souhaité : {tone}

Caractéristiques principales :
{features}

Mots-clés SEO à intégrer : {keywords}

La description doit :
1. Être engageante et persuasive
2. Intégrer naturellement les mots-clés SEO
3. Mettre en avant les caractéristiques principales
4. Adapter le ton au public cible
5. Être optimisée pour le référencement naturel
6. Être structurée avec des paragraphes courts et des puces pour les caractéristiques clés
7. Contenir uniquement le titre avec sa description, sans aucun autre texte ni de mots en gras.

Format de sortie souhaité :
- Un titre accrocheur
- Une description principale en 2-3 paragraphes
- Une liste de caractéristiques clés en puces
- Un appel à l'action final"""

    try:
        # Appel à l'API OpenAI avec la nouvelle syntaxe
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Vous êtes un expert en rédaction e-commerce spécialisé dans la création de descriptions de produits optimisées SEO."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Une erreur est survenue lors de la génération : {str(e)}")
        return None

# Formulaire principal
with st.form("product_description_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        product_name = st.text_input("Nom du produit")
        product_category = st.selectbox(
            "Catégorie du produit",
            ["Mode", "Décoration", "High-tech", "Alimentation", "Autre"]
        )
        target_audience = st.multiselect(
            "Public cible",
            ["Particuliers", "Professionnels", "Enfants", "Adolescents", "Seniors"]
        )
    
    with col2:
        brand_tone = st.selectbox(
            "Ton de marque",
            ["Professionnel", "Décontracté", "Luxe", "Écologique", "Technique"]
        )
        key_features = st.text_area(
            "Caractéristiques principales",
            placeholder="Listez les caractéristiques principales du produit, une par ligne"
        )
        keywords = st.text_input(
            "Mots-clés SEO",
            placeholder="Séparez les mots-clés par des virgules"
        )
    
    submitted = st.form_submit_button("Générer la description")

# Affichage du résultat
if submitted:
    if not product_name:
        st.error("Veuillez entrer le nom du produit.")
    else:
        # Vérifier la limite quotidienne
        if not check_daily_limit(st.session_state.email):
            st.error(f"Vous avez atteint la limite de {daily_limit} générations par jour. Revenez demain pour continuer.")
        else:
            with st.spinner("Génération de la description en cours..."):
                description = generate_product_description(
                    product_name,
                    product_category,
                    target_audience,
                    brand_tone,
                    key_features,
                    keywords
                )
                
                if description:
                    st.success("Description générée avec succès!")
                    # Stockage de la description dans la session state
                    st.session_state['current_description'] = description
                    st.session_state['current_product_name'] = product_name
                    st.session_state['show_feedback'] = True

# Affichage de la description actuelle si elle existe
if 'current_description' in st.session_state:
    st.markdown("### Description générée")
    st.code(st.session_state['current_description'], language=None)

# Formulaire de retour (séparé du formulaire principal)
if 'show_feedback' in st.session_state and st.session_state['show_feedback']:
    st.markdown("---")
    st.markdown("### Votre avis nous intéresse")
    with st.form("feedback_form"):
        satisfaction = st.radio(
            "Ce texte vous a-t-il satisfait ?",
            ["👍 Oui", "👎 Non"],
            horizontal=True
        )
        
        feedback_text = st.text_area(
            "Votre commentaire (optionnel)",
            placeholder="Dites-nous ce que vous pensez de cette description, ce qui vous a plu ou ce qui pourrait être amélioré."
        )
        
        feedback_submitted = st.form_submit_button("Envoyer le retour")
        
        if feedback_submitted:
            is_satisfied = satisfaction == "👍 Oui"
            if log_feedback(
                st.session_state['current_product_name'],
                st.session_state['current_description'],
                is_satisfied,
                feedback_text
            ):
                st.success("Merci pour votre retour !")
                # On ne supprime plus la description, on cache juste le formulaire de feedback
                st.session_state['show_feedback'] = False 