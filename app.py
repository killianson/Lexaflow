import streamlit as st
import openai
from dotenv import load_dotenv
import os
import pandas as pd
from datetime import datetime
import json

# Configuration de la page (doit être la première commande Streamlit)
st.set_page_config(
    page_title="Lexaflow - Générateur de Descriptions Produits",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

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
        # Création du dossier data s'il n'existe pas
        if not os.path.exists('data'):
            os.makedirs('data')
            st.write("Dossier data créé")
        
        # Création du fichier CSV s'il n'existe pas
        csv_file = 'data/feedback.csv'
        if not os.path.exists(csv_file):
            df = pd.DataFrame(columns=['timestamp', 'product_name', 'description', 'is_satisfied', 'feedback_text'])
            df.to_csv(csv_file, index=False)
            st.write("Fichier CSV créé")
        
        # Ajout du nouveau feedback
        new_feedback = pd.DataFrame({
            'timestamp': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            'product_name': [product_name],
            'description': [description],
            'is_satisfied': [is_satisfied],
            'feedback_text': [feedback_text]
        })
        
        new_feedback.to_csv(csv_file, mode='a', header=False, index=False)
        st.write("Feedback enregistré avec succès")
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

Format de sortie souhaité :
- Un titre accrocheur
- Une description principale en 2-3 paragraphes
- Une liste de caractéristiques clés en puces
- Un appel à l'action final"""

    try:
        # Appel à l'API OpenAI avec l'ancienne syntaxe
        response = openai.ChatCompletion.create(
            model="gpt-4",
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