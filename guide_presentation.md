# 🎮 Guide Complet — Projet Jeu de Nim
### Explication de A à Z + Questions du Professeur

---

## 🗂️ ÉTAPE 1 — Création du projet avec uv

### Ce qu'on a fait
```bash
uv init game
uv add pymysql matplotlib customtkinter
```

### Pourquoi
- `uv init game` → crée la structure du projet
- `uv add pymysql` → pour se connecter à MySQL et gérer la base de données
- `uv add matplotlib` → pour afficher les graphiques du dashboard
- `uv add customtkinter` → pour l'interface graphique moderne et arrondie

---

## 🗂️ ÉTAPE 2 — `settings.py` — Fichier de configuration

### Ce qu'on a fait
```python
DEFAULT_PILES  = [3, 5, 7]
LEVELS         = [1, 2, 3, 4]
LEVEL_NAMES    = {1: 'Debutant', 2: 'Intermediaire', 3: 'Avance', 4: 'Expert'}
MODE_JCJ       = 'JcJ'
MODE_JCIA      = 'JcIA'
...
```

### Pourquoi
Centraliser les constantes. Au lieu d'écrire `[3, 5, 7]` partout, on l'écrit une fois ici.

---

## 🗂️ ÉTAPE 3 — `database.py` — Accès aux données

### Ce qu'on a fait

#### 3.1 — La connexion globale
**Pourquoi c'est global** → Exactement comme le prof dans `dal.py`. Une seule connexion partagée.

#### 3.2 — Pattern commun à toutes les fonctions
```python
with connection.cursor() as cursor:
    try:
        cursor.execute('SQL...')
        connection.commit()
    except pymysql.Error as e:
        connection.rollback()
```
**Pourquoi `commit()` et `rollback()`** → `commit()` sauvegarde, `rollback()` annule si erreur.

#### 3.3 — `save_game(...)` — 3 requêtes
Enregistre la partie, met à jour le score du gagnant, et les défaites du perdant, le tout dans une seule transaction `try`.

---

## 🗂️ ÉTAPE 4 — `player.py` — Gestion des joueurs

### Ce qu'on a fait et pourquoi
Gère la création et l'affichage des joueurs.  
**Pourquoi `display_stats` recalcule-t-il les pourcentages ?** → Pour éviter de stocker des valeurs dérivées en base de données.

---

## 🗂️ ÉTAPE 5 — `enemy.py` — Intelligence Artificielle

### Ce qu'on a fait et pourquoi

#### 5.1 — Niveaux 1 et 2
- **Niveau 1** : Aléatoire.
- **Niveau 2** : Règles simples (réduit la plus grande pile).

#### 5.2 — `minimax(piles, is_maximizing)` — Niveau 3
**Pourquoi récursif** → Le Minimax explore tous les coups possibles jusqu'à la fin de la partie (comme `pgcd_euclid_rec`). 

#### 5.3 — `ai_nimsum(piles)` — Niveau 4
**Pourquoi XOR `^`** → Le Nim-Sum est le XOR de toutes les piles. On cherche le coup qui remet le Nim-Sum à 0 pour l'adversaire (stratégie optimale).

---

## 🗂️ ÉTAPE 6 — `main.py` — Programme console

Gère les menus via `os.system('cls')` et `match/case` comme dans `basis.py`, ainsi que les graphes Matplotlib (`plt.bar`, `plt.plot`).

---

## 🗂️ ÉTAPE 7 — `gui.py` — Interface Graphique (CustomTkinter)

### Ce qu'on a fait
Une interface complète avec boutons, saisies de texte, et dessin des jetons (Canvas) sans utiliser de POO (Programmation Orientée Objet).

### Pourquoi
- L'interface graphique était une exigence du projet. CustomTkinter permet un rendu moderne (arrondis, dark mode) très facilement, basé sur Tkinter.
- **Pourquoi pas de POO ?** Le cahier des charges l'interdit. On a donc géré les "écrans" avec une fonction pour chaque vue (`show_menu()`, `show_game()`) qui détruit les anciens widgets et crée les nouveaux, et des variables globales.

---

## 📌 RÉSUMÉ SIMPLIFIÉ

Le projet se compose de **6 fichiers** qui travaillent ensemble :

1. **`settings.py`** → configuration (constantes).
2. **`database.py`** → parle à MySQL.
3. **`player.py`** → calcule et gère les joueurs.
4. **`enemy.py`** → cerveau de l'IA.
5. **`main.py`** → jeu en mode console.
6. **`gui.py`** → jeu avec belle interface visuelle.

---

## ❓ QUESTIONS PROBABLES DU PROFESSEUR

### 🔵 Questions Générales

**Q : Pourquoi la connexion est définie en dehors des fonctions dans `database.py` ?**
> R : C'est le style qu'on a étudié dans `dal.py`. Une connexion globale partagée par toutes les fonctions. On n'a pas besoin de créer une nouvelle connexion à chaque appel.

**Q : Pourquoi `new_piles = list(piles)` dans Minimax ?**
> R : Pour copier la liste avant de la modifier. Si on modifie `piles` directement, tous les appels récursifs voient la même liste modifiée.

**Q : Qu'est-ce que l'opérateur ternaire ? Où l'avez-vous utilisé ?**
> R : `loser = player2 if winner == player1 else player1`. Si la condition est vraie → `player2`, sinon → `player1`.

### 🔵 Questions sur CustomTkinter (Interface Graphique)

**Q : Pourquoi vous n'avez pas utilisé de classes pour l'interface CustomTkinter ?**
> R : Le cahier des charges précisait "Pas de programmation orientée objet". J'ai donc créé des fonctions qui construisent l'interface (`show_menu`, `show_game`) et utilisent des variables globales pour conserver l'état du jeu.

**Q : Comment vous changez d'écran (Menu, Jeu, Victoire) dans Tkinter ?**
> R : Ma fonction `clear_content()` parcourt tous les éléments de la fenêtre (`content_frame.winfo_children()`) et les détruit (`widget.destroy()`). Ensuite, je recrée les nouveaux éléments (boutons, canvas) pour le nouvel écran.

**Q : Comment dessinez-vous les jetons ronds ?**
> R : J'utilise le composant `tk.Canvas` de Tkinter. Avec la méthode `create_oval()`, je peux dessiner des cercles pour représenter les jetons, et je les redessine à chaque fois qu'un joueur joue un coup.
