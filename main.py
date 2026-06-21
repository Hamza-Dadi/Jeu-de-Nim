import os
import time
from matplotlib import pyplot as plt
from settings import DEFAULT_PILES, MODE_JCJ, MODE_JCIA, LEVEL_NAMES
from database import create_tables, save_game, get_ranking, get_avg_duration, get_games_by_difficulty, get_score_evolution
from player import create_player, select_player, display_stats, display_history, display_all_players
from enemy import get_ai_move

# ============================================================
# AFFICHAGE DES PILES
# ============================================================
def display_piles(piles):
    print('\n' + '*'*30)
    for i in range(len(piles)):
        print(f'  pile {i+1}: ' + '|' * piles[i] + f'  ({piles[i]})')
    print('*'*30 + '\n')

# ============================================================
# VALIDATION D UN COUP
# ============================================================
def is_valid(piles, pile_index, count):
    if pile_index < 0 or pile_index >= len(piles):
        return False
    if count < 1 or count > piles[pile_index]:
        return False
    return True

# ============================================================
# DETECTION FIN DE PARTIE
# ============================================================
def is_game_over(piles):
    return sum(piles) == 0

# ============================================================
# COUP D UN JOUEUR HUMAIN
# ============================================================
def human_turn(piles, player_name):
    print(f'tour de {player_name}')
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

# ============================================================
# COUP DE L IA
# ============================================================
def ai_turn(piles, level):
    pile_index, count = get_ai_move(piles, level)
    print(f'IA ({LEVEL_NAMES[level]}) retire {count} objet(s) de la pile {pile_index+1}')
    piles[pile_index] = piles[pile_index] - count
    return piles

# ============================================================
# PARTIE JcJ
# ============================================================
def play_jcj(player1, player2, piles):
    start  = time.time()
    turn   = 0
    players = [player1, player2]
    while not is_game_over(piles):
        display_piles(piles)
        current = players[turn % 2]
        piles   = human_turn(piles, current)
        if is_game_over(piles):
            winner = current
            break
        turn = turn + 1
    duration = int(time.time() - start)
    display_piles(piles)
    print(f'\n*** {winner} a gagne ! ***\n')
    save_game(player1, player2, winner, MODE_JCJ, 0, duration, DEFAULT_PILES)

# ============================================================
# PARTIE JcIA
# ============================================================
def play_jcia(player1, level, piles):
    start  = time.time()
    turn   = 0
    while not is_game_over(piles):
        display_piles(piles)
        if turn % 2 == 0:
            piles = human_turn(piles, player1)
            if is_game_over(piles):
                winner = player1
                break
        else:
            piles = ai_turn(piles, level)
            if is_game_over(piles):
                winner = 'IA'
                break
        turn = turn + 1
    duration = int(time.time() - start)
    display_piles(piles)
    print(f'\n*** {winner} a gagne ! ***\n')
    save_game(player1, 'IA', winner, MODE_JCIA, level, duration, DEFAULT_PILES)

# ============================================================
# DASHBOARD STATISTIQUES
# ============================================================
def plot_ranking():
    results = get_ranking()
    x = []
    y = []
    for name, wins, score in results:
        x.append(name)
        y.append(score)
    plt.bar(x, y, width=0.4, color='green')
    plt.title('Classement des joueurs')
    plt.legend(['score'])
    plt.show()

def plot_difficulty():
    results = get_games_by_difficulty()
    x = []
    y = []
    for diff, count in results:
        x.append(LEVEL_NAMES.get(diff, str(diff)))
        y.append(count)
    plt.bar(x, y, width=0.4, color='blue')
    plt.title('Parties par niveau de difficulte')
    plt.legend(['nb parties'])
    plt.show()

def plot_score_evolution(name):
    results = get_score_evolution(name)
    x = []
    y = []
    score = 0
    for i in range(len(results)):
        date, winner = results[i]
        if winner == name:
            score = score + 10
        x.append(i+1)
        y.append(score)
    plt.plot(x, y, 'go-', label='score')
    plt.title('Evolution du score de ' + name)
    plt.legend()
    plt.show()

# ============================================================
# MENUS
# ============================================================
def menu_players():
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
                name = input('nom du joueur: ')
                create_player(name)
            case '2':
                display_all_players()
            case '3':
                name = input('nom du joueur: ')
                display_stats(name)
            case '4':
                name = input('nom du joueur: ')
                display_history(name)
            case _:
                break
        input('\nappuyer sur entree...')

def menu_dashboard():
    while True:
        os.system('cls')
        print('*'*10, 'Dashboard', '*'*10)
        print('''
          1- Classement des joueurs
          2- Parties par niveau de difficulte
          3- Evolution du score d un joueur
          4- Temps moyen des parties
          ''')
        choix = input('choix [1-4] ou autre pour retour: ')
        match choix:
            case '1':
                plot_ranking()
            case '2':
                plot_difficulty()
            case '3':
                name = input('nom du joueur: ')
                plot_score_evolution(name)
            case '4':
                print(f'temps moyen: {get_avg_duration()} secondes')
            case _:
                break
        input('\nappuyer sur entree...')

def menu_game():
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
                p1 = input('nom joueur 1: ')
                p2 = input('nom joueur 2: ')
                if select_player(p1) and select_player(p2):
                    piles = list(DEFAULT_PILES)
                    play_jcj(p1, p2, piles)
            case '2':
                p1 = input('nom joueur: ')
                if select_player(p1):
                    print('niveaux: 1-Debutant  2-Intermediaire  3-Avance  4-Expert')
                    try:
                        level = int(input('niveau de l IA [1-4]: '))
                        if level not in [1, 2, 3, 4]:
                            level = 1
                    except ValueError:
                        level = 1
                    piles = list(DEFAULT_PILES)
                    play_jcia(p1, level, piles)
            case _:
                break
        input('\nappuyer sur entree...')

# ============================================================
# MAIN
# ============================================================
if __name__ == '__main__':
    create_tables()
    while True:
        os.system('cls')
        print('*'*10, 'Jeu de Nim', '*'*10)
        print('''
          1- Nouvelle partie
          2- Gestion des joueurs
          3- Dashboard statistiques
          ''')
        choix = input('choix [1-3] ou autre pour quitter: ')
        match choix:
            case '1':
                menu_game()
            case '2':
                menu_players()
            case '3':
                menu_dashboard()
            case _:
                break
