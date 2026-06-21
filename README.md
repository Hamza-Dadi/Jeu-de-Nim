# 🎮 Jeu de Nim — avec Intelligence Artificielle
### Projet Python — ESISA 2026 | Hamza Dadi-Senhaji Mohammed

---

## 📋 Description

Application complète du **Jeu de Nim** développée en Python.  
Le jeu de Nim est un jeu de stratégie à deux joueurs. Au début de la partie, trois piles d'objets sont disposées (3, 5 et 7 objets). À tour de rôle, chaque joueur choisit une pile et retire un ou plusieurs objets. **Le joueur qui retire le dernier objet gagne**.

---

## 🗂️ Structure du projet

```
game/
├── main.py         ← programme principal (menus + logique du jeu + dashboard)
├── database.py     ← connexion MySQL et toutes les fonctions SQL
├── player.py       ← gestion des joueurs (créer, afficher, stats)
├── enemy.py        ← intelligence artificielle (4 niveaux)
├── settings.py     ← configuration (piles, niveaux, paramètres DB)
├── pyproject.toml  ← configuration du projet uv
└── .venv/          ← environnement virtuel
```

---

## ⚙️ Installation

### 1. Prérequis
- Python 3.10+
- MariaDB / MySQL
- uv (gestionnaire de paquets)

### 2. Installer les dépendances
```bash
uv add pymysql matplotlib
```

### 3. Créer la base de données
Se connecter à MariaDB et créer la base :
```bash
mariadb -u root -p
```
```sql
CREATE DATABASE nim_db;
exit
```

### 4. Lancer le projet
```bash
cd "c:\Users\msi\Desktop\Esisa\2eme Annee Esisa\Unix\Python\Projet\game"
uv run main.py
```
Les tables sont créées automatiquement au premier lancement.

---

## 🎮 Fonctionnalités

### Modes de jeu
| Mode | Description |
|---|---|
| **Joueur vs Joueur** | Deux joueurs humains s'affrontent |
| **Joueur vs IA** | Un joueur humain affronte l'ordinateur |

### Niveaux d'IA
| Niveau | Nom | Stratégie |
|---|---|---|
| 1 | Débutant | Coups aléatoires |
| 2 | Intermédiaire | Cible la plus grande pile |
| 3 | Avancé | Algorithme Minimax |
| 4 | Expert | Stratégie Nim-Sum (XOR) |

### Gestion des joueurs
- Créer un profil joueur
- Consulter les statistiques (victoires, défaites, score, taux)
- Consulter l'historique des parties

### Dashboard statistiques
- Classement des joueurs (graphe en barres)
- Parties par niveau de difficulté (graphe en barres)
- Evolution du score d'un joueur (courbe)
- Temps moyen des parties

---

## 🗄️ Base de données

### Table `t_player`
| Colonne | Type | Description |
|---|---|---|
| id | INT AUTO_INCREMENT | identifiant unique |
| name | VARCHAR(50) | nom du joueur |
| wins | INT | victoires |
| losses | INT | défaites |
| score | INT | score cumulé (+10 par victoire) |

### Table `t_game`
| Colonne | Type | Description |
|---|---|---|
| id | INT AUTO_INCREMENT | identifiant unique |
| player1 | VARCHAR(50) | joueur 1 |
| player2 | VARCHAR(50) | joueur 2 (ou 'IA') |
| winner | VARCHAR(50) | gagnant |
| mode | VARCHAR(10) | JcJ ou JcIA |
| difficulty | INT | niveau IA (0 si JcJ) |
| duration | INT | durée en secondes |
| piles | VARCHAR(50) | configuration des piles |
| date_game | DATETIME | date et heure de la partie |

---

## 📦 Packages utilisés

| Package | Version | Utilité |
|---|---|---|
| `pymysql` | 1.2.0 | connexion et requêtes MySQL |
| `matplotlib` | 3.11.0 | graphiques du dashboard |

---

## 🧠 Algorithmes implémentés

- **Random** : `random.choice()` + `random.randint()` (niveau 1)
- **Greedy** : ciblage de la plus grande pile (niveau 2)
- **Minimax** : exploration récursive de tous les états (niveau 3)
- **Nim-Sum** : stratégie mathématique XOR optimale (niveau 4)

---

## ▶️ Utilisation

```
Menu Principal
├── 1 - Nouvelle partie
│   ├── 1 - Joueur vs Joueur
│   └── 2 - Joueur vs IA (choisir niveau 1-4)
├── 2 - Gestion des joueurs
│   ├── 1 - Créer un joueur
│   ├── 2 - Afficher tous les joueurs
│   ├── 3 - Statistiques d'un joueur
│   └── 4 - Historique d'un joueur
└── 3 - Dashboard statistiques
    ├── 1 - Classement des joueurs
    ├── 2 - Parties par niveau
    ├── 3 - Evolution du score
    └── 4 - Temps moyen des parties
```

---

## 👨‍🎓 Informations

- **Auteur** : Hamza Dadi
- **Établissement** : ESISA
- **Année** : 2026
- **Matière** : Unix / Python
