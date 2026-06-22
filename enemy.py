import random
from settings import NOMS_NIVEAUX

# ============================================================
# NIVEAU 1 : aleatoire
# ============================================================
def ia_aleatoire(piles):
    piles_non_vides = [i for i in range(len(piles)) if piles[i] > 0]
    index_pile = random.choice(piles_non_vides)
    nb_objets  = random.randint(1, piles[index_pile])
    return index_pile, nb_objets

# ============================================================
# NIVEAU 2 : intermediaire (cible la pile la plus grande)
# ============================================================
def ia_intermediaire(piles):
    pile_max  = 0
    index_max = 0
    for i in range(len(piles)):
        if piles[i] > pile_max:
            pile_max  = piles[i]
            index_max = i
    nb_objets = random.randint(1, max(1, pile_max // 2))
    return index_max, nb_objets

# ============================================================
# NIVEAU 3 : avance (algorithme Minimax recursif)
# ============================================================
def ia_minimax(piles):
    meilleure_pile   = -1
    meilleur_nb      = -1
    meilleur_score   = -1
    for i in range(len(piles)):
        for nb in range(1, piles[i] + 1):
            nouvelles_piles = list(piles)
            nouvelles_piles[i] = nouvelles_piles[i] - nb
            score = minimax(nouvelles_piles, False)
            if score > meilleur_score:
                meilleur_score = score
                meilleure_pile = i
                meilleur_nb    = nb
    return meilleure_pile, meilleur_nb

def minimax(piles, est_maximisant):
    # cas de base : toutes les piles sont vides
    if sum(piles) == 0:
        if est_maximisant:
            return -1
        else:
            return 1
    if est_maximisant:
        meilleur = -1
        for i in range(len(piles)):
            for nb in range(1, piles[i] + 1):
                nouvelles_piles = list(piles)
                nouvelles_piles[i] = nouvelles_piles[i] - nb
                score = minimax(nouvelles_piles, False)
                if score > meilleur:
                    meilleur = score
        return meilleur
    else:
        meilleur = 1
        for i in range(len(piles)):
            for nb in range(1, piles[i] + 1):
                nouvelles_piles = list(piles)
                nouvelles_piles[i] = nouvelles_piles[i] - nb
                score = minimax(nouvelles_piles, True)
                if score < meilleur:
                    meilleur = score
        return meilleur

# ============================================================
# NIVEAU 4 : expert (strategie Nim-Sum avec XOR)
# ============================================================
def ia_nimsum(piles):
    nim_somme = 0
    for pile in piles:
        nim_somme = nim_somme ^ pile    # operateur XOR bit a bit
    if nim_somme == 0:
        return ia_aleatoire(piles)      # position perdante, joue au hasard
    for i in range(len(piles)):
        cible = piles[i] ^ nim_somme
        if cible < piles[i]:
            return i, piles[i] - cible
    return ia_aleatoire(piles)

# ============================================================
# DISPATCHER : choisit la bonne fonction selon le niveau
# ============================================================
def jouer_ia(piles, niveau):
    if niveau == 1:
        return ia_aleatoire(piles)
    elif niveau == 2:
        return ia_intermediaire(piles)
    elif niveau == 3:
        return ia_minimax(piles)
    else:
        return ia_nimsum(piles)

if __name__ == '__main__':
    piles = [3, 5, 7]
    print(f'aleatoire    : {ia_aleatoire(piles)}')
    print(f'intermediaire: {ia_intermediaire(piles)}')
    print(f'nimsum       : {ia_nimsum(piles)}')
