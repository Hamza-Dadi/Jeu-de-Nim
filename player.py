from database import ajouter_joueur, chercher_joueur, lister_joueurs, obtenir_statistiques, evolution_score

def creer_joueur(nom):
    existant = chercher_joueur(nom)
    if existant:
        print(f'joueur {nom} existe deja')
    else:
        ajouter_joueur(nom)
        print(f'joueur {nom} cree')

def selectionner_joueur(nom):
    joueur = chercher_joueur(nom)
    if joueur:
        return nom
    print(f'joueur {nom} introuvable')
    return None

def afficher_historique(nom):
    resultats = evolution_score(nom)
    if not resultats:
        print(f'aucune partie pour {nom}')
        return
    score = 0
    for date, gagnant in resultats:
        if gagnant == nom:
            score = score + 10
            print(f'{date} -- victoire  --> score: {score}')
        else:
            print(f'{date} -- defaite   --> score: {score}')

def afficher_stats(nom):
    resultats = obtenir_statistiques(nom)
    if not resultats:
        print(f'joueur {nom} introuvable')
        return
    victoires, defaites, score = resultats
    total = victoires + defaites
    if total > 0:
        taux = (victoires / total) * 100
    else:
        taux = 0
    print(f'joueur    : {nom}')
    print(f'victoires : {victoires}')
    print(f'defaites  : {defaites}')
    print(f'score     : {score}')
    print(f'taux      : {taux:.1f}%')

def afficher_tous_joueurs():
    resultats = lister_joueurs()
    if not resultats:
        print('aucun joueur enregistre')
        return
    for joueur in resultats:
        print(f'  {joueur[1]}  victoires={joueur[2]}  defaites={joueur[3]}  score={joueur[4]}')

if __name__ == '__main__':
    creer_joueur('Hamza')
    afficher_stats('Hamza')
    afficher_tous_joueurs()
