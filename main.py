# main.py
# Interface ligne de commande pour interagir avec l'application.

from dotenv import load_dotenv
from utils import init_resources, generate_response

# Charger les variables d'environnement
load_dotenv()

def main():
    """
    Interface en ligne de commande pour interagir avec l'application Document Q&A.
    """
    # Initialisation des ressources
    print("Initialisation des ressources...")
    retriever, chat_prompt_template, model, _ = init_resources("./docs/Solution_Cloud.md")
    print("Ressources initialisées avec succès.\n")

    print("Bienvenue dans l'interface Document Q&A CLI.")
    print("Posez vos questions sur le document chargé.")
    print("Tapez 'exit' pour quitter à tout moment.")

    while True:
        # Lecture de la requête utilisateur
        query = input("\nEntrez votre question (ou tapez 'exit' pour quitter) : ").strip()
        if query.lower() == 'exit':
            print("\nFin de la session. Merci d'avoir utilisé l'application !")
            break

        if query:
            # Génération de la réponse
            print("\nRecherche en cours...")
            response = generate_response(query, retriever, chat_prompt_template, model)
            if response:
                print("\nRéponse :\n", response)
            else:
                print("\nAucune réponse générée. Veuillez reformuler votre question.")
        else:
            print("Veuillez entrer une question valide.")

if __name__ == "__main__":
    main()
