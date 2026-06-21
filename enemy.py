import random
from settings import LEVEL_NAMES

def ai_random(piles):
    non_empty = [i for i in range(len(piles)) if piles[i] > 0]
    pile  = random.choice(non_empty)
    count = random.randint(1, piles[pile])
    return pile, count

def ai_intermediate(piles):
    max_pile  = 0
    max_index = 0
    for i in range(len(piles)):
        if piles[i] > max_pile:
            max_pile  = piles[i]
            max_index = i
    count = random.randint(1, max(1, max_pile // 2))
    return max_index, count

def ai_minimax(piles):
    best_pile  = -1
    best_count = -1
    best_score = -1
    for i in range(len(piles)):
        for count in range(1, piles[i]+1):
            new_piles = list(piles)
            new_piles[i] = new_piles[i] - count
            score = minimax(new_piles, False)
            if score > best_score:
                best_score = score
                best_pile  = i
                best_count = count
    return best_pile, best_count

def minimax(piles, is_maximizing):
    if sum(piles) == 0:
        if is_maximizing:
            return -1
        else:
            return 1
    if is_maximizing:
        best = -1
        for i in range(len(piles)):
            for count in range(1, piles[i]+1):
                new_piles = list(piles)
                new_piles[i] = new_piles[i] - count
                score = minimax(new_piles, False)
                if score > best:
                    best = score
        return best
    else:
        best = 1
        for i in range(len(piles)):
            for count in range(1, piles[i]+1):
                new_piles = list(piles)
                new_piles[i] = new_piles[i] - count
                score = minimax(new_piles, True)
                if score < best:
                    best = score
        return best

def ai_nimsum(piles):
    nim_sum = 0
    for p in piles:
        nim_sum = nim_sum ^ p
    if nim_sum == 0:
        return ai_random(piles)
    for i in range(len(piles)):
        target = piles[i] ^ nim_sum
        if target < piles[i]:
            return i, piles[i] - target
    return ai_random(piles)

def get_ai_move(piles, level):
    if level == 1:
        return ai_random(piles)
    elif level == 2:
        return ai_intermediate(piles)
    elif level == 3:
        return ai_minimax(piles)
    else:
        return ai_nimsum(piles)

if __name__ == '__main__':
    piles = [3, 5, 7]
    print(f'random      : {ai_random(piles)}')
    print(f'intermediate: {ai_intermediate(piles)}')
    print(f'nimsum      : {ai_nimsum(piles)}')
