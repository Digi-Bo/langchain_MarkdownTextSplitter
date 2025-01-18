# Optimisation du découpage en fragments de texte en markdown


## Les points clés 

1. **Respecter la structure logique du document (titres, sous-titres, paragraphes)**.
2. **Éviter les coupures qui interrompent des idées ou phrases importantes**.
3. **Réduire les chevauchements inutiles pour optimiser la pertinence des fragments**.

Voici une explication détaillée de la stratégie de les fonctions `MarkdownTextSplitter` et `RecursiveCharacterTextSplitter`. Ces fonctions se concentrent sur le découpage et l'optimisation des fragments de texte à partir d'un document Markdown, tout en respectant la structure logique et en évitant les fragments inutiles ou incohérents.

---

### Nos objectifs : 

1. **Préservation de la structure logique :**
   - Les séparateurs Markdown (`##`, `###`) sont prioritaires dans le découpage pour maintenir la hiérarchie du texte.

2. **Optimisation des tailles de fragments :**
   - Le processus garantit que chaque fragment est suffisamment long pour fournir un contexte utile, sans dépasser les limites de taille des modèles LLM.

3. **Élimination des déchets :**
   - Les fragments inutiles sont éliminés pour éviter des résultats inutiles ou redondants.

4. **Fusion adaptative :**
   - Les fragments courts mais significatifs sont combinés avec leurs voisins, tout en respectant la cohérence du texte.


---

### **Séquence des étapes**

#### **1. Charger le document**
```python
text_loader = TextLoader(file_path)
document = text_loader.load()
```

- Le `TextLoader` lit le fichier Markdown spécifié par `file_path` et retourne un objet `Document` contenant :
  - `page_content` : Le contenu texte du fichier.
  - `metadata` : Les métadonnées associées (par exemple, le chemin du fichier source).

#### **2. Découper avec `MarkdownTextSplitter`**
```python
initial_splitter = MarkdownTextSplitter(chunk_size=chunk_size * 4, chunk_overlap=chunk_overlap)
markdown_fragments = initial_splitter.split_documents(document)
```

- **But :** Réaliser un premier découpage basé sur la structure Markdown, en utilisant des titres (`##`, `###`, etc.) comme séparateurs prioritaires.
- **Paramètres :**
  - `chunk_size * 4` (par exemple, 2000 caractères si `chunk_size = 500`) : Génère de grands fragments initiaux pour minimiser les coupures inutiles.
  - `chunk_overlap` (par exemple, 50) : Définit le chevauchement entre les fragments pour préserver le contexte entre deux morceaux adjacents.
- **Résultat :** Une liste de fragments initiaux (`markdown_fragments`), chacun étant un objet `Document`.

#### **3. Découpage récursif pour fragments longs**
```python
recursive_splitter = RecursiveCharacterTextSplitter(
    chunk_size=chunk_size,
    chunk_overlap=chunk_overlap,
    separators=["\n### ", "\n## ", "\n\n", ".", " "]
)
final_fragments = []
for fragment in markdown_fragments:
    if len(fragment.page_content) > chunk_size:  # Vérification contre chunk_size
        sub_fragments = recursive_splitter.split_text(fragment.page_content)
        final_fragments.extend(
            [Document(page_content=sub.strip(), metadata=fragment.metadata) for sub in sub_fragments]
        )
    else:
        final_fragments.append(fragment)
```

- **But :** Redécouper récursivement les fragments trop longs (c.-à-d., dépassant `chunk_size`, par exemple 500 caractères).
- **Paramètres :**
  - `chunk_size` : Taille maximale des sous-fragments.
  - `chunk_overlap` : Chevauchement entre sous-fragments pour préserver le contexte.
  - `separators` : Liste de séparateurs utilisés pour découper les fragments en respectant la logique du texte (titres, paragraphes, phrases).
- **Processus :**
  - Chaque fragment de `markdown_fragments` est évalué.
  - Si sa taille dépasse `chunk_size`, il est redécoupé en sous-fragments via le découpeur récursif.
  - Les sous-fragments sont réinsérés dans la liste finale (`final_fragments`).

---

#### **4. Supprimer les fragments non significatifs**
```python
meaningful_fragments = [
    frag for frag in final_fragments
    if frag.page_content.strip() and len(frag.page_content.strip()) > 20
]
```

- **But :** Supprimer les fragments qui n’apportent aucune valeur (par exemple, des séparateurs `---` ou des fragments vides).
- **Critères :**
  - `frag.page_content.strip()` : Vérifie que le fragment n'est pas vide ou rempli uniquement d'espaces.
  - `len(frag.page_content.strip()) > 20` : Élimine les fragments trop courts pour avoir une valeur sémantique.

---

#### **5. Fusionner les fragments courts**
```python
optimized_fragments = []
i = 0
while i < len(meaningful_fragments):
    frag = meaningful_fragments[i]
    if len(frag.page_content) < chunk_size // 4:  # Si le fragment est court mais non trivial
        if i > 0 and not frag.page_content.startswith("#"):  # Fusion avec le précédent si possible
            optimized_fragments[-1].page_content += " " + frag.page_content.strip()
        elif i < len(meaningful_fragments) - 1:  # Fusion avec le suivant
            meaningful_fragments[i + 1].page_content = frag.page_content.strip() + " " + meaningful_fragments[i + 1].page_content
    else:
        optimized_fragments.append(frag)
    i += 1
```

- **But :** Combiner les fragments courts (par exemple, < 25 % de `chunk_size`) avec leurs voisins pour garantir qu’ils aient suffisamment de contexte.
- **Critères pour fusionner :**
  - Si le fragment est court, il est ajouté au fragment précédent (`optimized_fragments[-1]`) si possible.
  - Si le fragment court est en début de liste, il est fusionné avec le fragment suivant.
  - Les titres Markdown (`#`, `##`) ne sont jamais fusionnés avec des fragments précédents pour conserver la structure logique.
- **Résultat :** Une liste `optimized_fragments` contenant des fragments de taille et de contenu optimaux.

---

### **Récapitulatif des sorties**

1. **Chargement :**
   - Un document brut est chargé depuis un fichier Markdown.

2. **Découpage initial :**
   - Le document est séparé en fragments basés sur la structure Markdown avec une taille généreuse.

3. **Découpage récursif :**
   - Les fragments trop longs sont redécoupés en sous-fragments de taille uniforme.

4. **Nettoyage :**
   - Les fragments vides ou insignifiants sont supprimés.

5. **Fusion :**
   - Les fragments courts sont combinés avec leurs voisins pour maintenir un contexte sémantique.
