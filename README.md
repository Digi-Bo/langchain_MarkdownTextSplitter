
# 📘 Application de questions/réponses portant sur un document avec LangChain : stratégie de chunking sur du markdown

Ce programme permet de poser des questions sur un document préalablement chargé et d'obtenir des réponses pertinentes en utilisant un modèle d'intelligence artificielle. Le système exploite une base vectorielle pour rechercher le contexte approprié dans le document, puis génère une réponse via un modèle de chat. L'application propose deux interfaces :
- Une interface en ligne de commande (CLI) via `main.py`.
- Une interface web interactive via Streamlit avec `app.py`.


## Stratégie de chunking appliqué à du Markdown


### **`MarkdownTextSplitter`**



---

## 🌐 Créer et activer un environnement virtuel :

### **MacOS/Linux** :
```bash
python3 -m venv env
source env/bin/activate
```

### **Windows** :
```bash
python -m venv env
source env/bin/activate
```

---

## 🏗️ Installation des dépendances :

### Installer Python 3.6 ou une version supérieure

Utilisez `pip3` sur Mac ou Linux, et `pip` sous Windows :
```bash
pip install -r requirements.txt
pip install --upgrade langchain
```

---

## 🔑 Configuration des variables d'environnement :

Pour configurer correctement votre environnement, créez un fichier `.env` à la racine du projet et ajoutez les informations suivantes :

```env
# Clé API OpenAI pour accéder aux modèles d'OpenAI
OPENAI_API_KEY=sk-clé open ai

# Activer le suivi avancé (tracing) pour LangChain
LANGCHAIN_TRACING_V2=true

# URL de l'endpoint LangSmith pour le suivi des performances
LANGCHAIN_ENDPOINT="https://eu.api.smith.langchain.com"

# Clé API LangSmith pour le suivi
LANGSMITH_API_KEY=clé langsmith

# Nom du projet de suivi (facultatif, pour organiser vos traces)
LANGCHAIN_PROJECT="Test_project"
```



### Vérification :
Pour confirmer que les variables d'environnement sont bien définies, utilisez cette commande :
```bash
echo $OPENAI_API_KEY  # Sous MacOS/Linux
echo %OPENAI_API_KEY%  # Sous Windows
```


---

## ▶️ Lancer l'application en CLI :

Pour démarrer l'interface en ligne de commande :
```bash
python main.py
```

---

## ▶️ Lancer l'application Streamlit (localhost:8501) :

Pour démarrer l'interface web interactive :
```bash
streamlit run app.py
```

---

## 📄 Fonctionnement général :
1. Le document source (`state_of_the_union.txt`) est chargé et segmenté en fragments pour permettre une recherche efficace.
2. Une base vectorielle est construite à partir de ces fragments pour rechercher les parties pertinentes du document.
3. L'utilisateur pose une question via l'interface (CLI ou Streamlit).
4. Les fragments pertinents sont récupérés et utilisés comme contexte pour générer une réponse à l'aide du modèle de chat.
5. La réponse est affichée à l'utilisateur.
