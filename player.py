from database import insert_player, get_player, get_all_players, get_stats, get_score_evolution

def create_player(name):
    existing = get_player(name)
    if existing:
        print(f'joueur {name} existe deja')
    else:
        insert_player(name)
        print(f'joueur {name} cree')

def select_player(name):
    p = get_player(name)
    if p:
        return name
    print(f'joueur {name} introuvable')
    return None

def display_history(name):
    results = get_score_evolution(name)
    if not results:
        print(f'aucune partie pour {name}')
        return
    score = 0
    for date, winner in results:
        if winner == name:
            score = score + 10
            print(f'{date} -- victoire  --> score: {score}')
        else:
            print(f'{date} -- defaite   --> score: {score}')

def display_stats(name):
    results = get_stats(name)
    if not results:
        print(f'joueur {name} introuvable')
        return
    wins, losses, score = results
    total = wins + losses
    if total > 0:
        taux = (wins / total) * 100
    else:
        taux = 0
    print(f'joueur   : {name}')
    print(f'victoires: {wins}')
    print(f'defaites : {losses}')
    print(f'score    : {score}')
    print(f'taux     : {taux:.1f}%')

def display_all_players():
    results = get_all_players()
    if not results:
        print('aucun joueur')
        return
    for p in results:
        print(f'  {p[1]}  wins={p[2]}  losses={p[3]}  score={p[4]}')

if __name__ == '__main__':
    create_player('Hamza')
    display_stats('Hamza')
    display_all_players()
