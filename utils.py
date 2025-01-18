# utils.py

"""
Cette page regroupe les fonctions utilitaires pour gérer la logique métier de l'application.
Elle inclut des fonctions pour charger des documents, les découper en fragments optimisés,
créer une base vectorielle pour la recherche et configurer les modèles d'IA.

- `initialize_openai_key` : Vérifie et retourne la clé API OpenAI.
- `load_and_split_document` : Charge un document Markdown, le découpe en fragments cohérents et les optimise.
- `create_vector_store` : Crée une base vectorielle pour permettre la recherche contextuelle dans les fragments.
- `setup_templates_and_model` : Configure les prompts et initialise un modèle de chat basé sur OpenAI.
- `generate_response` : Génère une réponse en utilisant les documents pertinents et un modèle d'IA.
- `init_resources` : Initialise toutes les ressources nécessaires (documents, base vectorielle, modèles) 
                     pour l'application en un seul appel.
"""



from langchain.schema import Document
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import MarkdownTextSplitter, RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain.prompts.chat import (
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
    ChatPromptTemplate
)
from langchain_openai.chat_models import ChatOpenAI


import os

def initialize_openai_key():
    """
    Vérifie la clé OpenAI et la retourne.
    """
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY n'est pas défini. Veuillez le configurer dans votre environnement.")
    return openai_api_key




def load_and_split_document(file_path, chunk_size=500, chunk_overlap=50):
    """
    Charge un document Markdown, le découpe en fragments optimisés et améliore leur qualité.

    Cette fonction permet de lire un document Markdown depuis un fichier, de le diviser en morceaux (ou fragments)
    de taille raisonnable pour un traitement par des modèles de langage. Elle élimine les fragments inutiles
    et fusionne ceux qui sont trop courts pour produire une liste finale de fragments cohérents et utiles.

    Args:
        file_path (str): Le chemin vers le fichier Markdown à charger.
        chunk_size (int): La taille maximale souhaitée d'un fragment, en nombre de caractères.
                          Les fragments dépassant cette taille seront redécoupés.
        chunk_overlap (int): Le chevauchement entre les fragments, pour garantir que le contexte
                             important soit préservé entre deux morceaux adjacents.

    Returns:
        list[Document]: Une liste d'objets `Document`. Chaque document contient un fragment de texte
                        optimisé pour un traitement ultérieur.
    """

    # Charger le document Markdown depuis le fichier spécifié
    # `TextLoader` est utilisé pour lire le contenu brut du fichier.
    text_loader = TextLoader(file_path)
    document = text_loader.load()

    # Étape 1 : Découpage initial basé sur la structure Markdown
    # `MarkdownTextSplitter` divise le texte en fragments basés sur des titres Markdown (`##`, `###`, etc.).
    # Les fragments initiaux sont plus grands pour réduire les coupures inutiles.
    initial_splitter = MarkdownTextSplitter(chunk_size=chunk_size * 4, chunk_overlap=chunk_overlap)
    markdown_fragments = initial_splitter.split_documents(document)

    # Étape 2 : Découpage récursif des fragments longs
    # Les fragments dépassant `chunk_size` sont redécoupés en sous-fragments plus petits.
    # On utilise des séparateurs spécifiques (titres, paragraphes, phrases).
    recursive_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n### ", "\n## ", "\n\n", ".", " "]
    )
    final_fragments = []
    for fragment in markdown_fragments:
        if len(fragment.page_content) > chunk_size:  # Si le fragment est trop long
            sub_fragments = recursive_splitter.split_text(fragment.page_content)
            # Ajouter les sous-fragments comme nouveaux objets `Document`
            final_fragments.extend(
                [Document(page_content=sub.strip(), metadata=fragment.metadata) for sub in sub_fragments]
            )
        else:
            # Ajouter directement les fragments courts ou de taille raisonnable
            final_fragments.append(fragment)

    # Étape 3 : Supprimer les fragments non significatifs
    # On élimine les fragments trop courts (par exemple, contenant seulement des séparateurs).
    meaningful_fragments = [
        frag for frag in final_fragments
        if frag.page_content.strip() and len(frag.page_content.strip()) > 20
    ]

    # Étape 4 : Fusionner les fragments courts
    # Les fragments très courts (par exemple, < 25 % de `chunk_size`) sont fusionnés avec leurs voisins.
    optimized_fragments = []
    i = 0
    while i < len(meaningful_fragments):
        frag = meaningful_fragments[i]
        if len(frag.page_content) < chunk_size // 4:  # Si le fragment est court
            if i > 0 and not frag.page_content.startswith("#"):  # Fusion avec le précédent si possible
                optimized_fragments[-1].page_content += " " + frag.page_content.strip()
            elif i < len(meaningful_fragments) - 1:  # Fusion avec le suivant
                meaningful_fragments[i + 1].page_content = frag.page_content.strip() + " " + meaningful_fragments[i + 1].page_content
        else:
            # Ajouter le fragment directement s'il est de taille correcte
            optimized_fragments.append(frag)
        i += 1

    # Retourner la liste finale de fragments optimisés
    return optimized_fragments



















def create_vector_store(documents, openai_api_key):
    """
    Crée une base vectorielle à partir des documents.
    """
    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
    db = Chroma.from_documents(documents, embeddings)
    return db.as_retriever()


def setup_templates_and_model(openai_api_key):
    """
    Définir les templates et initialiser le modèle de chat.
    """
    # Définir les templates de prompts
    template = (
        "You are a helpful assistant. Based on the following context:\n\n{context}\n\n"
        "Answer the question: {question}"
    )
    system_message_prompt = SystemMessagePromptTemplate.from_template(template)
    human_message_prompt = HumanMessagePromptTemplate.from_template("{question}")
    chat_prompt_template = ChatPromptTemplate.from_template(template)

    # Initialiser le modèle de chat
    model = ChatOpenAI(openai_api_key=openai_api_key)

    return (chat_prompt_template, model)

def generate_response(query, retriever, chat_prompt_template, model):
    """
    Génère une réponse basée sur la question et les documents pertinents.
    """
    try:
        # Recherche des documents pertinents
        relevant_docs = retriever.invoke(query)

        # Construire un contexte
        context = "\n\n".join([doc.page_content for doc in relevant_docs]) if relevant_docs else "No relevant context found."

        # Générer une réponse
        messages = chat_prompt_template.format_messages(context=context, question=query)
        raw_response = model.invoke(messages)
        return raw_response.content if hasattr(raw_response, 'content') else str(raw_response)
    except Exception as e:
        return f"Erreur : {e}"




def init_resources(file_path):
    """
    Initialise toutes les ressources nécessaires pour l'application.
    """
    # Initialiser la clé OpenAI
    openai_api_key = initialize_openai_key()

    # Charger et découper le document
    documents = load_and_split_document(file_path)

    # Créer une base vectorielle
    retriever = create_vector_store(documents, openai_api_key)

    # Configurer les templates et le modèle
    templates, model = setup_templates_and_model(openai_api_key)

    return retriever, templates, model, documents
