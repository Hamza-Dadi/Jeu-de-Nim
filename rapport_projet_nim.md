# 📋 Rapport Détaillé — Projet Jeu de Nim
### Hamza Dadi — ESISA 2026

---

## ✅ VÉRIFICATION STYLE DU PROF — 100% CONFORME

Aucune notion extérieure au cours ou aux exercices n'a été utilisée. L'interface graphique a été construite avec CustomTkinter sans aucune classe, respectant la contrainte de la programmation procédurale.

---

## 📁 FICHIER 1 — `settings.py`

### Rôle
Centralise toutes les **constantes** du projet pour ne pas les répéter dans chaque fichier.

### Contenu et explication

```python
DEFAULT_PILES  = [3, 5, 7]
```
**Liste** Python → configuration classique du jeu de Nim : 3 piles avec 3, 5 et 7 objets.  
Concept vu : **listes** (`basis.py`, `algo.py`)

```python
LEVEL_NAMES = {1: 'Debutant', 2: 'Intermediaire', 3: 'Avance', 4: 'Expert'}
```
**Dictionnaire** → associe un numéro de niveau à son nom.  
Concept vu : **dict** (`auto_complete.py`)

```python
MODE_JCJ  = 'JcJ'
MODE_JCIA = 'JcIA'
```
**Variables string** → modes de jeu utilisés comme constantes.  
Concept vu : **variables** (`basis.py`)

```python
DB_HOST = 'localhost'
DB_PORT = 3306
DB_USER = 'root'
DB_PASSWORD = ''
DB_NAME = 'nim_db'
```
**Paramètres de connexion MySQL** → importés dans `database.py`.  
Concept vu : **variables** + **import depuis un module** (`app.py`)

### ✅ Style du prof
> Pas de `if __name__` car c'est un simple fichier de configuration, comme la convention Python.

---

## 📁 FICHIER 2 — `database.py`

### Rôle
**Couche d'accès aux données** (DAL — Data Access Layer).  
Gère toute la communication avec la base de données MySQL.  
Style identique au fichier `dal.py` du prof.

### Connexion globale
```python
import pymysql
from settings import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME

connection = pymysql.Connection(
    host=DB_HOST,
    port=DB_PORT,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME,
)
```
**Connexion globale** au niveau du module → une seule connexion partagée par toutes les fonctions.  
Concept vu : **pymysql**, **connexion globale** (`dal.py`)

### Pattern commun à toutes les fonctions
```python
with connection.cursor() as cursor:
    try:
        cursor.execute('SQL ...')
        connection.commit()
    except pymysql.Error as e:
        print(e)
        connection.rollback()
```
- `with connection.cursor() as cursor` → ouvre un curseur SQL automatiquement fermé
- `try/except pymysql.Error` → capture les erreurs SQL
- `connection.commit()` → valide la transaction
- `connection.rollback()` → annule si erreur  
Concept vu : **try/except/rollback/commit** (`dal.py`)

---

### Fonction `create_tables()`
Crée les deux tables si elles n'existent pas encore :

**Table `t_player`** :
| Colonne | Type | Description |
|---|---|---|
| `id` | INT AUTO_INCREMENT | identifiant unique |
| `name` | VARCHAR(50) | nom du joueur |
| `wins` | INT DEFAULT 0 | nombre de victoires |
| `losses` | INT DEFAULT 0 | nombre de défaites |
| `score` | INT DEFAULT 0 | score cumulé |

**Table `t_game`** :
| Colonne | Type | Description |
|---|---|---|
| `id` | INT AUTO_INCREMENT | identifiant unique |
| `player1` | VARCHAR(50) | nom joueur 1 |
| `player2` | VARCHAR(50) | nom joueur 2 (ou 'IA') |
| `winner` | VARCHAR(50) | nom du gagnant |
| `mode` | VARCHAR(10) | 'JcJ' ou 'JcIA' |
| `difficulty` | INT | niveau IA (0 si JcJ) |
| `duration` | INT | durée en secondes |
| `piles` | VARCHAR(50) | configuration des piles |
| `date_game` | DATETIME | date automatique |

Concept vu : **CREATE TABLE IF NOT EXISTS**, **AUTO_INCREMENT** (`dal.py`)

---

### Fonction `insert_player(name)`
```python
cursor.execute('INSERT INTO t_player(name) VALUES(%s)', (name,))
connection.commit()
```
Insère un nouveau joueur.  
`%s` → protection contre les injections SQL.  
Concept vu : **INSERT avec %s** (`dal.py`)

---

### Fonction `get_player(name)`
```python
cursor.execute('SELECT * FROM t_player WHERE name=%s', (name,))
results = cursor.fetchone()
```
Retourne un seul joueur par son nom.  
`fetchone()` → retourne **un seul tuple** (une seule ligne).  
Concept vu : **SELECT WHERE**, **fetchone()** (`dal.py`)

---

### Fonction `get_all_players()`
```python
cursor.execute('SELECT * FROM t_player')
results = cursor.fetchall()
```
Retourne tous les joueurs.  
`fetchall()` → retourne une **liste de tuples**.  
Concept vu : **fetchall()** (`dal.py`)

---

### Fonction `save_game(player1, player2, winner, mode, difficulty, duration, piles)`
```python
cursor.execute('INSERT INTO t_game(...) VALUES(%s,%s,%s,%s,%s,%s,%s)', (...))
cursor.execute('UPDATE t_player SET wins=wins+1, score=score+10 WHERE name=%s', (winner,))
loser = player2 if winner == player1 else player1
cursor.execute('UPDATE t_player SET losses=losses+1 WHERE name=%s', (loser,))
connection.commit()
```
- Enregistre la partie dans `t_game`
- Met à jour les victoires et le score du gagnant
- Met à jour les défaites du perdant
- `loser = player2 if winner == player1 else player1` → **opérateur ternaire** Python  
Concept vu : **UPDATE SQL**, **ternaire** (`basis.py`)

---

### Fonction `get_stats(name)`
Retourne les statistiques d'un joueur → tuple `(wins, losses, score)`.

---

### Fonction `get_ranking()`
```python
cursor.execute('SELECT name, wins, score FROM t_player ORDER BY score DESC')
results = cursor.fetchall()
```
Retourne le classement trié par score décroissant.  
Concept vu : **ORDER BY** (cours SQL)

---

### Fonction `get_avg_duration()`
Retourne la durée moyenne des parties.  
`AVG()` → fonction d'agrégation SQL.

---

### Fonction `get_games_by_difficulty()`
```python
cursor.execute(
    'SELECT difficulty, COUNT(*) FROM t_game WHERE mode=%s GROUP BY difficulty',
    ('JcIA',)
)
```
Retourne le nombre de parties par niveau de difficulté.  
Concept vu : **GROUP BY**, **COUNT(*)** (cours SQL + `dal.py`)

---

### Fonction `get_score_evolution(name)`
Retourne toutes les parties d'un joueur triées par date → pour tracer l'évolution du score.

---

## 📁 FICHIER 3 — `player.py`

### Rôle
Gestion des joueurs côté application (au-dessus de `database.py`).  
Style identique à `dashboard.py` du prof qui importe depuis `dal.py`.

### Imports
```python
from database import insert_player, get_player, get_all_players, get_stats, get_score_evolution
```
Concept vu : **import depuis un module** (`app.py`, `dashboard.py`)

---

### Fonction `create_player(name)`
```python
def create_player(name):
    existing = get_player(name)
    if existing:
        print(f'joueur {name} existe deja')
    else:
        insert_player(name)
        print(f'joueur {name} cree')
```
Vérifie si le joueur existe avant de le créer → évite les doublons.  
Concept vu : **if/else**, **f-strings** (`basis.py`)

---

### Fonction `select_player(name)`
Vérifie qu'un joueur existe avant de lancer une partie.  
Retourne `name` si trouvé, `None` sinon.  
Concept vu : **return**, **None** (`functions..py`)

---

### Fonction `display_history(name)`
```python
score = 0
for date, winner in results:
    if winner == name:
        score = score + 10
        print(f'{date} -- victoire  --> score: {score}')
    else:
        print(f'{date} -- defaite   --> score: {score}')
```
Parcourt les parties avec `for date, winner in results` → **déstructuration de tuples**.  
Recalcule le score à chaque partie.  
Concept vu : **for**, **tuples**, **f-strings** (`auto_complete.py`, `dashboard.py`)

---

### Fonction `display_stats(name)`
```python
wins, losses, score = results
total = wins + losses
if total > 0:
    taux = (wins / total) * 100
else:
    taux = 0
print(f'taux: {taux:.1f}%')
```
- **Déstructuration** du tuple résultat
- Calcul du taux de victoire en pourcentage
- `{taux:.1f}%` → formatage à 1 décimale  
Concept vu : **f-strings avec formatage** (`basis.py`)

---

### Fonction `display_all_players()`
```python
for p in results:
    print(f'  {p[1]}  wins={p[2]}  losses={p[3]}  score={p[4]}')
```
Parcourt tous les joueurs et affiche leurs stats.  
`p[1]`, `p[2]`... → accès aux colonnes par index (tuple MySQL).  
Concept vu : **indexation de tuples** (`dashboard.py`)

---

## 📁 FICHIER 4 — `enemy.py`

### Rôle
Intelligence Artificielle du jeu — 4 niveaux de difficulté.  
Toutes les fonctions retournent un **tuple `(pile_index, count)`**.

---

### Fonction `ai_random(piles)` — Niveau 1
```python
non_empty = [i for i in range(len(piles)) if piles[i] > 0]
pile  = random.choice(non_empty)
count = random.randint(1, piles[pile])
return pile, count
```
- **List comprehension** → liste des piles non vides
- `random.choice(L)` → choisit un élément aléatoire dans L
- `random.randint(a, b)` → entier aléatoire entre a et b inclus  
Concept vu : **list comprehension** (`prime.py`, `algo.py`), **random** (Python standard)

---

### Fonction `ai_intermediate(piles)` — Niveau 2
```python
max_pile  = 0
max_index = 0
for i in range(len(piles)):
    if piles[i] > max_pile:
        max_pile  = piles[i]
        max_index = i
count = random.randint(1, max(1, max_pile // 2))
return max_index, count
```
- Trouve la pile la plus grande (comme `max` dans `polynome.py`)
- Retire entre 1 et la moitié de la pile → stratégie simple
- `//` → division entière  
Concept vu : **for i in range**, **if comparaison**, **division entière** (`algo.py`)

---

### Fonctions `ai_minimax(piles)` et `minimax(piles, is_maximizing)` — Niveau 3

**`ai_minimax`** :
Teste tous les coups possibles et choisit celui avec le meilleur score Minimax.  
`list(piles)` → copie la liste pour ne pas modifier l'original.  
Concept vu : **for imbriqués**, **listes** (`algo.py`, `prime.py`)

**`minimax`** (récursif) :
```python
def minimax(piles, is_maximizing):
    if sum(piles) == 0:
        if is_maximizing:
            return -1
        else:
            return 1
    ...
    return minimax(new_piles, False)  # appel récursif
```
- **Récursivité** → comme `pgcd_euclid_rec` dans `algo.py`
- Cas de base : `sum(piles) == 0` → partie terminée
- `is_maximizing=True` → tour de l'IA (maximise) / `False` → tour du joueur (minimise)  
Concept vu : **récursivité** (`algo.py`)

---

### Fonction `ai_nimsum(piles)` — Niveau 4 (Expert)
```python
nim_sum = 0
for p in piles:
    nim_sum = nim_sum ^ p
```
- `^` → **opérateur XOR bit à bit**
- Le **Nim-Sum** = XOR de toutes les piles
- Si `nim_sum == 0` → position perdante → joue aléatoirement
- Sinon → trouve la pile où `piles[i] XOR nim_sum < piles[i]` et retire la différence  
Concept vu : **opérateur XOR `^`** (cours + partiel Q8)

---

### Fonction `get_ai_move(piles, level)`
**Dispatcher** → appelle la bonne fonction selon le niveau.  
Concept vu : **if/elif/else** (`basis.py`)

---

## 📁 FICHIER 5 — `main.py`

### Rôle
Point d'entrée principal du jeu en mode console. Contient la logique du jeu en texte, les menus et le dashboard.  
Style identique à `basis.py` (menus) + `dashboard.py` (graphiques).

### Imports
```python
import os
import time
from matplotlib import pyplot as plt
```
Concept vu : **import os** (`linux_cmd.py`), **import time** (`algo.py`), **matplotlib** (`dashboard.py`), **import depuis modules** (`app.py`)

---

### Fonction `display_piles(piles)`
```python
for i in range(len(piles)):
    print(f'  pile {i+1}: ' + '|' * piles[i] + f'  ({piles[i]})')
```
Affiche les piles visuellement avec des `|`.  
`'|' * piles[i]` → répétition de string.  
Concept vu : **répétition string** `'*'*10` (`basis.py`)

---

### Fonction `is_valid(piles, pile_index, count)`
Valide un coup du joueur.  
Concept vu : **if/return bool** (`prime.py`, `auto_complete.py`)

---

### Fonction `human_turn(piles, player_name)`
```python
while True:
    try:
        pile_index = int(input('choisir une pile (1,2,3...): ')) - 1
        count      = int(input('combien d objets retirer ? : '))
        if is_valid(piles, pile_index, count):
            piles[pile_index] = piles[pile_index] - count
            return piles
        else:
            print('coup invalide, reessayer')
    except ValueError:
        print('entrer un nombre valide')
```
- `while True` → boucle infinie jusqu'à un coup valide
- `try/except ValueError` → si l'utilisateur entre une lettre au lieu d'un nombre
- `int(input(...))` → conversion entrée utilisateur  
Concept vu : **while True**, **try/except ValueError**, **input/int** (`basis.py`, `linux_cmd.py`)

---

### Fonctions Dashboard

**`plot_ranking()`** :
```python
x = []
y = []
for name, wins, score in results:
    x.append(name)
    y.append(score)
plt.bar(x, y, width=0.4, color='green')
plt.title('Classement des joueurs')
plt.legend(['score'])
plt.show()
```
Graphe en barres du classement.  
Concept vu : **x=[], y=[], plt.bar** (`dashboard.py`)

---

## 📁 FICHIER 6 — `gui.py`

### Rôle
Interface graphique moderne et premium (CustomTkinter) avec thème sombre (Dark Mode) et bordures arrondies. Ce fichier remplit l'exigence "Interface graphique" du cahier des charges avec un résultat professionnel.

### Principes utilisés
- **CustomTkinter** pour l'affichage moderne, les boutons arrondis, les zones de texte fluides et la boucle d'événements (`root.mainloop()`).
- **Composant Canvas** : Utilisé pour dessiner manuellement les piles et les jetons avec `create_rectangle`, `create_oval` et `create_text`.
- **Aucune classe** : toute la logique utilise des variables globales (`global state, piles, ...`) et des fonctions (`def show_menu()`, `def show_game()`) pour respecter la contrainte de ne pas utiliser la programmation orientée objet. Les vues sont changées en détruisant les anciens widgets et en créant les nouveaux.
- **Réutilisation de la logique** : importe les mêmes fonctions de `database.py`, `player.py`, et `enemy.py` que le `main.py`.

---

## 🔍 VÉRIFICATION FINALE — CONCEPTS UTILISÉS

| Concept | Fichier prof | Utilisé dans |
|---|---|---|
| Variables, types | `basis.py` | tous les fichiers |
| f-strings | `basis.py` | tous les fichiers |
| if/elif/else | `basis.py` | tous les fichiers |
| while True | `basis.py` | `main.py`, `gui.py` |
| match/case | `basis.py` | `main.py` |
| for i in range | `basis.py` | `enemy.py`, `main.py`, `gui.py` |
| os.system('cls') | `basis.py` | `main.py` |
| Récursivité | `algo.py` | `enemy.py` (minimax) |
| time.perf_counter | `algo.py` | `main.py`, `gui.py` (time.time) |
| List comprehension | `prime.py` | `enemy.py` |
| Listes, append, sum | `linux_cmd.py` | partout |
| try/except | `linux_cmd.py` | `main.py`, `database.py` |
| pymysql connexion globale | `dal.py` | `database.py` |
| cursor.execute / fetchall | `dal.py` | `database.py` |
| commit / rollback | `dal.py` | `database.py` |
| matplotlib plt.bar | `dashboard.py` | `main.py` |
| import depuis modules | `app.py` | tous les fichiers |
| Opérateur XOR ^ | partiel Q8 | `enemy.py` |

---

## 📝 RÉSUMÉ LONG

Le projet **Jeu de Nim** est une application complète développée en Python dans le style exact du professeur M. Lahmer. Il est organisé en **6 modules** distincts.

**`settings.py`** est le fichier de configuration qui centralise toutes les constantes du projet.

**`database.py`** est la couche DAL (Data Access Layer), construite exactement comme le fichier `dal.py` du professeur. Il contient une connexion globale à MySQL et 9 fonctions qui gèrent les deux tables. Chaque fonction utilise le pattern `try/except pymysql.Error` et `rollback()`.

**`player.py`** gère les joueurs côté application et calcule les statistiques.

**`enemy.py`** implémente l'intelligence artificielle en 4 niveaux croissants (Random, Règles simples, Minimax récursif, XOR optimal).

**`main.py`** est le cœur console de l'application avec la logique des menus en texte et des graphiques Matplotlib.

**`gui.py`** est l'interface graphique CustomTkinter, ajoutée pour répondre aux critères du projet. Elle utilise un design premium (Dark Mode) et une logique totalement sans classe.

Tous les concepts utilisés ont été étudiés en classe. **Aucune classe (POO)** n'a été utilisée.

---

## 📌 RÉSUMÉ COURT

Le projet Jeu de Nim est organisé en 6 fichiers :

| Fichier | Rôle | Style du prof |
|---|---|---|
| `settings.py` | constantes et config DB | variables Python |
| `database.py` | connexion MySQL + CRUD | `dal.py` |
| `player.py` | gestion joueurs | `dashboard.py` |
| `enemy.py` | IA 4 niveaux (random/règles/minimax/XOR) | `algo.py` |
| `main.py` | menus + jeu console + dashboard | `basis.py` + `dashboard.py` |
| `gui.py` | interface graphique moderne CustomTkinter | (exigence du projet) |

**Concepts clés** : connexion globale pymysql, try/except rollback, menus, matplotlib bar/plot, récursivité minimax, XOR nim-sum.  
**Aucune classe** utilisée. **100% conforme aux consignes.** ✅
