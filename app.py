import streamlit as st
import os
import csv
from dotenv import load_dotenv
from datetime import datetime
from openai import OpenAI
import gspread
from oauth2client.service_account import ServiceAccountCredentials


def log_feedback_to_gsheet(topic, keywords, tone, is_satisfied, feedback_text):
    try:
        # Définir les autorisations nécessaires
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name("google_creds.json", scope)
        client = gspread.authorize(creds)

        # Ouvrir ou créer la feuille de calcul
        try:
            sheet = client.open("Lexaflow Feedback").sheet1
        except:
            sheet = client.create("Lexaflow Feedback").sheet1
            sheet.append_row(["Timestamp", "Sujet", "Mots-clés", "Ton", "Satisfait", "Feedback"])

        # Ajouter une nouvelle ligne
        row = [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), topic, keywords, tone, is_satisfied, feedback_text]
        sheet.append_row(row)

        return True
    except Exception as e:
        st.error(f"Erreur lors de l’enregistrement du feedback : {e}")
        return False
    



# Chargement de la clé API depuis le .env
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialisation du compteur de génération
if "counter" not in st.session_state:
    st.session_state.counter = 0

# Titres
st.set_page_config(page_title="Lexaflow - Générateur SEO IA", layout="centered")
st.title("🧠 Générateur d’articles de blog SEO avec l’IA")
st.markdown("Entrez les informations ci-dessous pour générer un article optimisé automatiquement.")

# Formulaire utilisateur
with st.form("article_form"):
    topic = st.text_input("📝 Sujet de l’article", placeholder="Ex : Comment choisir une lampe design ?")
    keywords = st.text_input("🔍 Mots-clés SEO (séparés par des virgules)", placeholder="lampe moderne, ambiance lumineuse")
    tone = st.selectbox("🎙 Ton souhaité", ["Professionnel", "Amical", "Informatif", "Inspirationnel"])
    notes = st.text_area("🧾 Quelque chose à préciser sur votre activité ?", placeholder="Ex : Nous sommes un magasin de déco basé à Marseille.")
    
    submitted = st.form_submit_button("🚀 Générer l’article")

# Limite d’usage
if st.session_state.counter >= 5:
    st.warning("🚫 Vous avez atteint la limite de 5 générations. Merci d’avoir testé la bêta !")
    submitted = False

# Génération de contenu
if submitted and topic:
    with st.spinner("Rédaction de votre article en cours..."):

        prompt = f"""
Tu es un rédacteur web spécialisé en SEO. Écris un article de blog de 600 à 800 mots structuré (titres H2/H3) sur le sujet suivant : "{topic}".
- Intègre les mots-clés suivants : {keywords}
- Adopte un ton {tone.lower()}
- Voici des précisions sur l'entreprise : {notes}
- Commence par une introduction engageante, puis structure le corps de l’article en plusieurs parties claires.
- Termine par une conclusion utile.
        """

        try:
            response = client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1200
            )
            content = response.choices[0].message.content
            st.session_state.counter += 1

            # Affichage
            st.markdown("### ✨ Résultat généré")
            st.write(content)
            st.success("✅ Article généré avec succès !")

        except Exception as e:
            st.error(f"❌ Une erreur est survenue : {e}")

# Feedback
st.divider()
st.subheader("💬 Laissez un feedback (optionnel)")

with st.form("feedback_form"):
    is_satisfied = st.radio("Êtes-vous satisfait du contenu ?", ["Oui", "Non"], horizontal=True)
    feedback_text = st.text_area("Un commentaire à nous faire ?", placeholder="Dites-nous ce que vous en pensez...")
    send = st.form_submit_button("📩 Envoyer")

if send:
    if log_feedback_to_gsheet(topic, keywords, tone, is_satisfied, feedback_text):
        st.success("Merci pour votre retour 🙏")