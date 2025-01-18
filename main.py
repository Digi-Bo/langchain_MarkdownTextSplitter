# main.py
# Interface ligne de commande pour interagir avec l'application.

from dotenv import load_dotenv
load_dotenv()


from utils import initialize_model_and_data, generate_response

def main():
    retriever, chat_prompt_template, model, _ = initialize_model_and_data()

    print("Bienvenue dans l'interface Document Q&A CLI.")
    while True:
        query = input("\nEntrez votre question (ou tapez 'exit' pour quitter) : ").strip()
        if query.lower() == 'exit':
            print("Fin de la session. Merci d'avoir utilisé l'application !")
            break

        if query:
            print("\nRecherche en cours...")
            response = generate_response(query, retriever, chat_prompt_template, model)
            if response:
                print("\nRéponse :\n", response)
            else:
                print("\nAucune réponse générée.")
        else:
            print("Veuillez entrer une question valide.")

if __name__ == "__main__":
    main()
