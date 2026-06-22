import os
import time
from matplotlib import pyplot as plt
from settings import PILES_DEFAUT, MODE_JCJ, MODE_JCIA, NOMS_NIVEAUX
from database import creer_tables, enregistrer_partie, classement_joueurs, duree_moyenne_parties, parties_par_niveau, evolution_score
from player import creer_joueur, selectionner_joueur, afficher_stats, afficher_historique, afficher_tous_joueurs
from enemy import jouer_ia

# ============================================================
# AFFICHAGE DES PILES
# ============================================================
def afficher_piles(piles):
    print('\n' + '*'*30)
    for i in range(len(piles)):
        print(f'  pile {i+1}: ' + '|' * piles[i] + f'  ({piles[i]})')
    print('*'*30 + '\n')

# ============================================================
# VALIDATION D UN COUP
# ============================================================
def coup_valide(piles, index_pile, nb_objets):
    if index_pile < 0 or index_pile >= len(piles):
        return False
    if nb_objets < 1 or nb_objets > piles[index_pile]:
        return False
    return True

# ============================================================
# DETECTION FIN DE PARTIE
# ============================================================
def partie_terminee(piles):
    return sum(piles) == 0

# ============================================================
# COUP D UN JOUEUR HUMAIN
# ============================================================
def tour_joueur(piles, nom_joueur):
    print(f'tour de {nom_joueur}')
    while True:
        try:
            index_pile = int(input('choisir une pile (1,2,3...): ')) - 1
            nb_objets  = int(input('combien d objets retirer ? : '))
            if coup_valide(piles, index_pile, nb_objets):
                piles[index_pile] = piles[index_pile] - nb_objets
                return piles
            else:
                print('coup invalide, reessayer')
        except ValueError:
            print('entrer un nombre valide')

# ============================================================
# COUP DE L IA
# ============================================================
def tour_ia(piles, niveau):
    index_pile, nb_objets = jouer_ia(piles, niveau)
    print(f'IA ({NOMS_NIVEAUX[niveau]}) retire {nb_objets} objet(s) de la pile {index_pile+1}')
    piles[index_pile] = piles[index_pile] - nb_objets
    return piles

# ============================================================
# PARTIE JcJ
# ============================================================
def jouer_jcj(joueur1, joueur2, piles):
    debut  = time.time()
    tour   = 0
    joueurs = [joueur1, joueur2]
    while not partie_terminee(piles):
        afficher_piles(piles)
        joueur_actuel = joueurs[tour % 2]
        piles = tour_joueur(piles, joueur_actuel)
        if partie_terminee(piles):
            gagnant = joueur_actuel
            break
        tour = tour + 1
    duree = int(time.time() - debut)
    afficher_piles(piles)
    print(f'\n*** {gagnant} a gagne ! ***\n')
    enregistrer_partie(joueur1, joueur2, gagnant, MODE_JCJ, 0, duree, PILES_DEFAUT)

# ============================================================
# PARTIE JcIA
# ============================================================
def jouer_jcia(joueur1, niveau, piles):
    debut  = time.time()
    tour   = 0
    while not partie_terminee(piles):
        afficher_piles(piles)
        if tour % 2 == 0:
            piles = tour_joueur(piles, joueur1)
            if partie_terminee(piles):
                gagnant = joueur1
                break
        else:
            piles = tour_ia(piles, niveau)
            if partie_terminee(piles):
                gagnant = 'IA'
                break
        tour = tour + 1
    duree = int(time.time() - debut)
    afficher_piles(piles)
    print(f'\n*** {gagnant} a gagne ! ***\n')
    enregistrer_partie(joueur1, 'IA', gagnant, MODE_JCIA, niveau, duree, PILES_DEFAUT)

# ============================================================
# DASHBOARD GRAPHIQUES
# ============================================================
def graphe_classement():
    resultats = classement_joueurs()
    x = []
    y = []
    for nom, victoires, score in resultats:
        x.append(nom)
        y.append(score)
    plt.bar(x, y, width=0.4, color='green')
    plt.title('Classement des joueurs')
    plt.legend(['score'])
    plt.show()

def graphe_niveaux():
    resultats = parties_par_niveau()
    x = []
    y = []
    for niveau, nb in resultats:
        x.append(NOMS_NIVEAUX.get(niveau, str(niveau)))
        y.append(nb)
    plt.bar(x, y, width=0.4, color='blue')
    plt.title('Parties par niveau de difficulte')
    plt.legend(['nb parties'])
    plt.show()

def graphe_evolution_score(nom):
    resultats = evolution_score(nom)
    x = []
    y = []
    score = 0
    for i in range(len(resultats)):
        date, gagnant = resultats[i]
        if gagnant == nom:
            score = score + 10
        x.append(i + 1)
        y.append(score)
    plt.plot(x, y, 'go-', label='score')
    plt.title('Evolution du score de ' + nom)
    plt.legend()
    plt.show()

# ============================================================
# MENUS
# ============================================================
def menu_joueurs():
    while True:
        os.system('cls')
        print('*'*10, 'Gestion Joueurs', '*'*10)
        print('''
          1- Creer un joueur
          2- Afficher tous les joueurs
          3- Statistiques d un joueur
          4- Historique d un joueur
          ''')
        choix = input('choix [1-4] ou autre pour retour: ')
        match choix:
            case '1':
                nom = input('nom du joueur: ')
                creer_joueur(nom)
            case '2':
                afficher_tous_joueurs()
            case '3':
                nom = input('nom du joueur: ')
                afficher_stats(nom)
            case '4':
                nom = input('nom du joueur: ')
                afficher_historique(nom)
            case _:
                break
        input('\nappuyer sur entree...')

def menu_tableaux():
    while True:
        os.system('cls')
        print('*'*10, 'Tableaux de bord', '*'*10)
        print('''
          1- Classement des joueurs
          2- Parties par niveau de difficulte
          3- Evolution du score d un joueur
          4- Temps moyen des parties
          ''')
        choix = input('choix [1-4] ou autre pour retour: ')
        match choix:
            case '1':
                graphe_classement()
            case '2':
                graphe_niveaux()
            case '3':
                nom = input('nom du joueur: ')
                graphe_evolution_score(nom)
            case '4':
                print(f'temps moyen: {duree_moyenne_parties()} secondes')
            case _:
                break
        input('\nappuyer sur entree...')

def menu_partie():
    while True:
        os.system('cls')
        print('*'*10, 'Nouvelle Partie', '*'*10)
        print('''
          1- Joueur contre Joueur
          2- Joueur contre IA
          ''')
        choix = input('choix [1-2] ou autre pour retour: ')
        match choix:
            case '1':
                j1 = input('nom joueur 1: ')
                j2 = input('nom joueur 2: ')
                if selectionner_joueur(j1) and selectionner_joueur(j2):
                    piles = list(PILES_DEFAUT)
                    jouer_jcj(j1, j2, piles)
            case '2':
                j1 = input('nom joueur: ')
                if selectionner_joueur(j1):
                    print('niveaux: 1-Debutant  2-Intermediaire  3-Avance  4-Expert')
                    try:
                        niveau = int(input('niveau de l IA [1-4]: '))
                        if niveau not in [1, 2, 3, 4]:
                            niveau = 1
                    except ValueError:
                        niveau = 1
                    piles = list(PILES_DEFAUT)
                    jouer_jcia(j1, niveau, piles)
            case _:
                break
        input('\nappuyer sur entree...')

# ============================================================
# MAIN
# ============================================================
if __name__ == '__main__':
    creer_tables()
    while True:
        os.system('cls')
        print('*'*10, 'Jeu de Nim', '*'*10)
        print('''
          1- Nouvelle partie
          2- Gestion des joueurs
          3- Tableaux de bord
          ''')
        choix = input('choix [1-3] ou autre pour quitter: ')
        match choix:
            case '1':
                menu_partie()
            case '2':
                menu_joueurs()
            case '3':
                menu_tableaux()
            case _:
                break
