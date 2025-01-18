from langchain_community.document_loaders import TextLoader
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain.text_splitter import MarkdownTextSplitter
from langchain.prompts.chat import (
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain.prompts import ChatPromptTemplate
from langchain_openai.chat_models import ChatOpenAI
from langchain_community.vectorstores import Chroma
import os

def initialize_model_and_data():
    """
    Initialise et configure les ressources nécessaires.
    """
    # Vérification de la clé API OpenAI
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY n'est pas défini. Veuillez le configurer dans votre environnement.")

    # Charger le document
    markdown_path = "./docs/Solution_Cloud.md"
    text_loader = TextLoader(markdown_path)
    document = text_loader.load()

    # Diviser le document en fragments
    text_splitter = MarkdownTextSplitter(
        chunk_size=60,
        chunk_overlap=0
    )
    documents = text_splitter.split_documents(document)

    # Créer une base vectorielle
    db = Chroma.from_documents(documents, OpenAIEmbeddings(openai_api_key=openai_api_key))
    retriever = db.as_retriever()

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

    return retriever, chat_prompt_template, model, documents

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
