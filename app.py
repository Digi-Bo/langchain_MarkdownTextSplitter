# app.py
# Interface principale de l'application via Streamlit.

import streamlit as st
from dotenv import load_dotenv
from utils import init_resources, generate_response
import warnings

# Ignorer les avertissements pour des logs plus clairs
warnings.filterwarnings("ignore")

# Charger les variables d'environnement
load_dotenv()

# Configuration de la page Streamlit
st.set_page_config(page_title="Chattez avec un document", layout="wide")

# Initialisation des ressources avec mise en cache
@st.cache_resource
def load_resources():
    """
    Fonction pour charger les ressources initiales avec caching Streamlit.
    """
    return init_resources("./docs/presentation-vps.md")

retriever, chat_prompt_template, model, documents = load_resources()

# Interface utilisateur
st.title("🗂️ Chattez avec un document")
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
    for i, doc in enumerate(documents[:5]):  # Limite l'affichage à 5 fragments
        st.write(f"**Fragment {i + 1}** : {doc}")

# Bouton pour afficher tous les fragments
if st.button("Afficher tous les fragments"):
    st.write("### Liste complète des fragments :")
    for i, doc in enumerate(documents):  # Afficher tous les fragments
        st.write(f"**Fragment {i + 1}** : {doc}")
