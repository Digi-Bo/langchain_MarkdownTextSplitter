# app.py
# Interface principale de l'application via Streamlit.

import streamlit as st
from dotenv import load_dotenv
import warnings
from utils import initialize_model_and_data, generate_response

# Ignorer les avertissements pour des logs plus clairs
warnings.filterwarnings("ignore")

# Charger les variables d'environnement
load_dotenv()

# Configuration de la page Streamlit
st.set_page_config(page_title="Document Q&A", layout="wide")

# Fonction pour initialiser les modèles et les données (mise en cache)
@st.cache_resource
def init_resources():
    return initialize_model_and_data()

# Initialiser les ressources nécessaires
retriever, chat_prompt_template, model, documents = init_resources()

# Interface utilisateur
st.title("🗂️ Document Q&A Chat")
st.write("Posez des questions sur le document chargé.")

# Champ de saisie pour la question
query = st.text_input("Votre question :", placeholder="Entrez votre question ici...")

# Traitement de la requête utilisateur
if query:
    with st.spinner("Recherche des documents pertinents..."):
        response = generate_response(query, retriever, chat_prompt_template, model)
    st.write("### Réponse :")
    if response:
        st.success(response)
    else:
        st.error("Aucune réponse générée. Vérifiez les paramètres ou la question.")

# Option pour afficher un résumé des fragments
if st.checkbox("Afficher le résumé du document chargé"):
    st.write("### Résumé des fragments :")
    for i, doc in enumerate(documents[:5]):  # Affichage limité à 5 fragments
        st.write(f"**Fragment {i + 1}** : {doc.page_content}")
