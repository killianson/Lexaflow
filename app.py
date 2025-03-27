import streamlit as st
import openai
from dotenv import load_dotenv
import os

# Chargement des variables d'environnement
load_dotenv()

# Configuration de la clé API OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

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
        # Appel à l'API OpenAI
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

# Configuration de la page
st.set_page_config(
    page_title="lixie.ai - Générateur de Descriptions Produits",
    page_icon="✨",
    layout="wide"
)

# Titre et description
st.title("✨ lixie.ai")
st.markdown("""
    ### Générateur intelligent de descriptions produits
    Créez des descriptions de produits optimisées SEO en quelques clics.
""")

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
                st.markdown("### Description générée")
                st.markdown(description)
                
                # Bouton pour copier la description
                st.button("Copier la description", 
                         on_click=lambda: st.write("Description copiée dans le presse-papiers!")) 