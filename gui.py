import pygame
import sys
import time
from settings import DEFAULT_PILES, LEVEL_NAMES, MODE_JCJ, MODE_JCIA
from database import create_tables, save_game, get_ranking
from player import create_player
from enemy import get_ai_move

# ============================================================
# PALETTE BLEU NUIT + OR
# ============================================================
BG          = (8,   12,  28)
PANEL       = (18,  28,  60)
PANEL2      = (22,  35,  75)
GOLD        = (212, 175, 55)
GOLD_LIGHT  = (255, 215, 0)
WHITE       = (240, 245, 255)
GRAY        = (90,  100, 135)
DARK        = (12,  18,  40)
GREEN       = (46,  213, 115)
RED         = (220, 60,  75)
BLUE_ACC    = (80,  140, 255)
PILE_COLS   = [(210, 55,  75),   # rubis
               (55,  130, 230),  # saphir
               (46,  200, 110)]  # emeraude

# ============================================================
# ETAT DU JEU
# ============================================================
state          = 'menu'
piles          = []
player1        = ''
player2        = ''
mode           = ''
level          = 1
turn           = 0
winner         = ''
selected_pile  = -1
selected_count = 1
start_time     = 0
input_step     = 0
input_text     = ''
msg            = ''
msg_color      = RED

font_title = None
font_big   = None
font_med   = None
font_small = None
font_tiny  = None

# ============================================================
# FONTES
# ============================================================
def init_fonts():
    global font_title, font_big, font_med, font_small, font_tiny
    font_title = pygame.font.SysFont('Georgia', 52, bold=True)
    font_big   = pygame.font.SysFont('Georgia', 36, bold=True)
    font_med   = pygame.font.SysFont('Arial',   26)
    font_small = pygame.font.SysFont('Arial',   20)
    font_tiny  = pygame.font.SysFont('Arial',   16)

# ============================================================
# HELPERS DESSIN
# ============================================================
def draw_text(screen, text, x, y, font, color=WHITE, center=True):
    surf = font.render(str(text), True, color)
    rect = surf.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    screen.blit(surf, rect)

def draw_panel(screen, x, y, w, h, color=PANEL, border=GOLD, radius=14):
    pygame.draw.rect(screen, color,  (x, y, w, h), border_radius=radius)
    pygame.draw.rect(screen, border, (x, y, w, h), 2, border_radius=radius)

def draw_button(screen, text, x, y, w, h, font, filled=True):
    if filled:
        pygame.draw.rect(screen, GOLD,  (x, y, w, h), border_radius=10)
        surf = font.render(str(text), True, DARK)
    else:
        pygame.draw.rect(screen, PANEL, (x, y, w, h), border_radius=10)
        pygame.draw.rect(screen, GOLD,  (x, y, w, h), 2, border_radius=10)
        surf = font.render(str(text), True, GOLD)
    rect = surf.get_rect(center=(x + w // 2, y + h // 2))
    screen.blit(surf, rect)
    return pygame.Rect(x, y, w, h)

def draw_separator(screen, y, x1=60, x2=740):
    pygame.draw.line(screen, GOLD, (x1, y), (x2, y), 1)

def draw_background(screen):
    screen.fill(BG)
    for i in range(0, 800, 80):
        pygame.draw.line(screen, (15, 22, 48), (i, 0), (i, 750), 1)
    for j in range(0, 750, 80):
        pygame.draw.line(screen, (15, 22, 48), (0, j), (800, j), 1)

def draw_token(screen, cx, cy, color, size=22):
    pygame.draw.circle(screen, DARK,  (cx, cy), size + 3)
    pygame.draw.circle(screen, color, (cx, cy), size)
    pygame.draw.circle(screen, GOLD,  (cx, cy), size, 2)
    pygame.draw.circle(screen, (255, 255, 255, 80), (cx - size // 3, cy - size // 3), size // 4)

def draw_pile(screen, count, index, selected):
    cx = 185 + index * 225
    base_y = 510
    color  = PILE_COLS[index]

    panel_x = cx - 68
    panel_y = 160
    panel_w = 136
    panel_h = 395
    border  = GOLD_LIGHT if selected else GOLD
    thick   = 3 if selected else 1
    pygame.draw.rect(screen, PANEL2, (panel_x, panel_y, panel_w, panel_h), border_radius=14)
    pygame.draw.rect(screen, border, (panel_x, panel_y, panel_w, panel_h), thick, border_radius=14)

    for i in range(count):
        draw_token(screen, cx, base_y - i * 46, color)

    label_color = GOLD_LIGHT if selected else GRAY
    draw_text(screen, f'Pile {index + 1}', cx, 568, font_small, label_color)
    draw_text(screen, f'({count})',         cx, 588, font_tiny,  label_color)

# ============================================================
# ECRAN MENU
# ============================================================
def draw_menu(screen):
    draw_background(screen)
    draw_panel(screen, 150, 50, 500, 100, PANEL, GOLD, 16)
    draw_text(screen, 'JEU  DE  NIM', 400, 100, font_title, GOLD_LIGHT)
    draw_separator(screen, 165)
    draw_text(screen, 'Strategie · Intelligence · Victoire', 400, 195, font_tiny, GRAY)

    btn1 = draw_button(screen, 'Nouvelle Partie',   250, 250, 300, 55, font_med, filled=True)
    btn2 = draw_button(screen, 'Statistiques',      250, 325, 300, 55, font_med, filled=False)
    btn3 = draw_button(screen, 'Quitter',           250, 400, 300, 55, font_med, filled=False)

    draw_separator(screen, 480)
    draw_text(screen, 'Piles : 3 — 5 — 7  |  Le dernier qui joue gagne', 400, 500, font_tiny, GRAY)
    return btn1, btn2, btn3

# ============================================================
# ECRAN SETUP
# ============================================================
def draw_setup(screen):
    draw_background(screen)
    draw_panel(screen, 120, 30, 560, 70, PANEL, GOLD, 14)
    draw_text(screen, 'NOUVELLE PARTIE', 400, 65, font_big, GOLD_LIGHT)
    draw_separator(screen, 110)
    btn_back = draw_button(screen, '← Retour', 25, 25, 130, 38, font_tiny, filled=False)

    if input_step == 0:
        draw_text(screen, 'Choisir le mode de jeu', 400, 180, font_med, WHITE)
        btn1 = draw_button(screen, '⚔  Joueur  vs  Joueur', 175, 240, 450, 65, font_med, filled=True)
        btn2 = draw_button(screen, '🤖  Joueur  vs  IA',    175, 330, 450, 65, font_med, filled=False)
        return btn1, btn2, None, None, None, btn_back

    elif input_step == 1:
        draw_text(screen, 'Nom du Joueur 1', 400, 185, font_med, GOLD)
        draw_panel(screen, 175, 220, 450, 52, PANEL2, GOLD, 10)
        draw_text(screen, input_text + '|', 400, 246, font_med, WHITE)
        btn1 = draw_button(screen, 'Confirmer  →', 275, 305, 250, 52, font_med, filled=True)
        return btn1, None, None, None, None, btn_back

    elif input_step == 2 and mode == MODE_JCJ:
        draw_text(screen, f'Joueur 1 : {player1}', 400, 145, font_small, GREEN)
        draw_text(screen, 'Nom du Joueur 2', 400, 200, font_med, GOLD)
        draw_panel(screen, 175, 235, 450, 52, PANEL2, GOLD, 10)
        draw_text(screen, input_text + '|', 400, 261, font_med, WHITE)
        btn1 = draw_button(screen, 'Lancer la partie  →', 250, 325, 300, 52, font_med, filled=True)
        return btn1, None, None, None, None, btn_back

    elif input_step == 2 and mode == MODE_JCIA:
        draw_text(screen, f'Joueur : {player1}', 400, 140, font_small, GREEN)
        draw_text(screen, 'Niveau de difficulte', 400, 190, font_med, GOLD)
        btn1 = draw_button(screen, '1  —  Debutant',      175, 230, 450, 52, font_med, filled=False)
        btn2 = draw_button(screen, '2  —  Intermediaire', 175, 300, 450, 52, font_med, filled=False)
        btn3 = draw_button(screen, '3  —  Avance',        175, 370, 450, 52, font_med, filled=False)
        btn4 = draw_button(screen, '4  —  Expert',        175, 440, 450, 52, font_med, filled=True)
        return btn1, btn2, btn3, btn4, None, btn_back

    return None, None, None, None, None, btn_back

# ============================================================
# ECRAN JEU
# ============================================================
def draw_game(screen):
    draw_background(screen)
    current = get_current_player()

    # header
    draw_panel(screen, 10, 8, 780, 60, PANEL, GOLD, 12)
    draw_text(screen, f'{player1}  vs  {player2}', 300, 38, font_small, GRAY)
    draw_text(screen, f'Tour de :  {current}', 580, 38, font_small, GOLD_LIGHT)

    for i in range(len(piles)):
        draw_pile(screen, piles[i], i, i == selected_pile)

    draw_separator(screen, 610)
    draw_text(screen, 'Cliquer sur une pile pour la selectionner', 400, 630, font_tiny, GRAY)

    btn_moins = None
    btn_plus  = None
    btn_jouer = None

    if selected_pile >= 0:
        label = f'Pile {selected_pile + 1} selectionnee   |   Retirer : {selected_count}'
        draw_text(screen, label, 380, 660, font_small, WHITE)
        btn_moins = draw_button(screen, '−', 180, 685, 55, 45, font_big, filled=False)
        btn_plus  = draw_button(screen, '+', 250, 685, 55, 45, font_big, filled=False)
        btn_jouer = draw_button(screen, 'Jouer', 330, 685, 160, 45, font_med, filled=True)

    if msg:
        draw_text(screen, msg, 400, 725, font_tiny, msg_color)

    btn_quit = draw_button(screen, 'Abandonner', 608, 685, 155, 45, font_small, filled=False)
    return btn_moins, btn_plus, btn_jouer, btn_quit

# ============================================================
# ECRAN VICTOIRE
# ============================================================
def draw_win(screen):
    draw_background(screen)
    draw_panel(screen, 100, 100, 600, 350, PANEL, GOLD, 20)
    draw_separator(screen, 190, 120, 680)
    draw_text(screen, '★  VICTOIRE  ★',    400, 155, font_title, GOLD_LIGHT)
    draw_separator(screen, 200, 120, 680)
    draw_text(screen, f'{winner}  a  gagne !', 400, 270, font_big, WHITE)
    btn1 = draw_button(screen, 'Rejouer',  175, 400, 200, 55, font_med, filled=True)
    btn2 = draw_button(screen, '← Menu',  430, 400, 200, 55, font_med, filled=False)
    return btn1, btn2

# ============================================================
# ECRAN STATISTIQUES
# ============================================================
def draw_stats(screen):
    draw_background(screen)
    draw_panel(screen, 80, 30, 640, 70, PANEL, GOLD, 14)
    draw_text(screen, 'CLASSEMENT', 400, 65, font_big, GOLD_LIGHT)
    draw_separator(screen, 115)

    draw_panel(screen, 80, 130, 640, 40, PANEL2, GOLD, 8)
    draw_text(screen, '#',         140, 150, font_small, GOLD)
    draw_text(screen, 'Joueur',    280, 150, font_small, GOLD)
    draw_text(screen, 'Victoires', 490, 150, font_small, GOLD)
    draw_text(screen, 'Score',     630, 150, font_small, GOLD)

    results = get_ranking()
    y = 185
    for i in range(len(results)):
        name, wins, score = results[i]
        col = GOLD_LIGHT if i == 0 else WHITE
        draw_text(screen, str(i + 1),  140, y, font_small, col)
        draw_text(screen, name,        280, y, font_small, col)
        draw_text(screen, str(wins),   490, y, font_small, GREEN)
        draw_text(screen, str(score),  630, y, font_small, BLUE_ACC)
        pygame.draw.line(screen, PANEL2, (90, y + 18), (710, y + 18), 1)
        y = y + 40

    btn1 = draw_button(screen, '← Menu', 275, 620, 250, 55, font_med, filled=False)
    return btn1

# ============================================================
# LOGIQUE JEU
# ============================================================
def get_current_player():
    if mode == MODE_JCJ:
        return [player1, player2][turn % 2]
    return player1 if turn % 2 == 0 else 'IA'

def is_game_over():
    return sum(piles) == 0

def is_valid(pile_index, count):
    if pile_index < 0 or pile_index >= len(piles):
        return False
    if count < 1 or count > piles[pile_index]:
        return False
    return True

def apply_move(pile_index, count):
    piles[pile_index] = piles[pile_index] - count

def start_game():
    global piles, turn, selected_pile, selected_count, start_time, winner, msg
    piles          = list(DEFAULT_PILES)
    turn           = 0
    selected_pile  = -1
    selected_count = 1
    start_time     = time.time()
    winner         = ''
    msg            = ''

# ============================================================
# BOUCLE PRINCIPALE
# ============================================================
def main():
    global state, player1, player2, mode, level, turn
    global winner, selected_pile, selected_count
    global input_step, input_text, msg, msg_color

    pygame.init()
    screen = pygame.display.set_mode((800, 750))
    pygame.display.set_caption('Jeu de Nim')
    clock = pygame.time.Clock()
    init_fonts()
    create_tables()

    while True:
        clock.tick(60)

        # ======= MENU =======
        if state == 'menu':
            btn1, btn2, btn3 = draw_menu(screen)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if btn1.collidepoint(event.pos):
                        state = 'setup'
                        input_step = 0
                        input_text = ''
                        msg = ''
                    if btn2.collidepoint(event.pos):
                        state = 'stats'
                    if btn3.collidepoint(event.pos):
                        pygame.quit()
                        sys.exit()

        # ======= SETUP =======
        elif state == 'setup':
            btns = draw_setup(screen)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if input_step in [1, 2] and not (input_step == 2 and mode == MODE_JCIA):
                        if event.key == pygame.K_BACKSPACE:
                            input_text = input_text[:-1]
                        elif event.key != pygame.K_RETURN:
                            input_text = input_text + event.unicode
                if event.type == pygame.MOUSEBUTTONDOWN:
                    btn_back = btns[5]
                    if btn_back and btn_back.collidepoint(event.pos):
                        if input_step == 0:
                            state = 'menu'
                        else:
                            input_step = input_step - 1
                            input_text = ''
                    elif input_step == 0:
                        if btns[0] and btns[0].collidepoint(event.pos):
                            mode = MODE_JCJ
                            input_step = 1
                            input_text = ''
                        if btns[1] and btns[1].collidepoint(event.pos):
                            mode = MODE_JCIA
                            input_step = 1
                            input_text = ''
                    elif input_step == 1:
                        if btns[0] and btns[0].collidepoint(event.pos):
                            if input_text.strip():
                                player1 = input_text.strip()
                                create_player(player1)
                                input_step = 2
                                input_text = ''
                    elif input_step == 2 and mode == MODE_JCJ:
                        if btns[0] and btns[0].collidepoint(event.pos):
                            if input_text.strip():
                                player2 = input_text.strip()
                                create_player(player2)
                                start_game()
                                state = 'game'
                    elif input_step == 2 and mode == MODE_JCIA:
                        player2 = 'IA'
                        for lvl in [1, 2, 3, 4]:
                            if btns[lvl - 1] and btns[lvl - 1].collidepoint(event.pos):
                                level = lvl
                                start_game()
                                state = 'game'

        # ======= GAME =======
        elif state == 'game':
            current = get_current_player()
            if mode == MODE_JCIA and current == 'IA':
                pygame.time.delay(700)
                pile_index, count = get_ai_move(piles, level)
                apply_move(pile_index, count)
                msg       = f'IA ({LEVEL_NAMES[level]}) retire {count} objet(s) de la pile {pile_index + 1}'
                msg_color = BLUE_ACC
                if is_game_over():
                    winner   = 'IA'
                    duration = int(time.time() - start_time)
                    save_game(player1, player2, winner, mode, level, duration, DEFAULT_PILES)
                    state = 'win'
                else:
                    turn          = turn + 1
                    selected_pile  = -1
                    selected_count = 1

            btn_moins, btn_plus, btn_jouer, btn_quit = draw_game(screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for i in range(len(piles)):
                        cx = 185 + i * 225
                        if abs(event.pos[0] - cx) < 68 and 160 < event.pos[1] < 560:
                            if piles[i] > 0:
                                selected_pile  = i
                                selected_count = 1
                                msg = ''
                    if btn_moins and btn_moins.collidepoint(event.pos):
                        if selected_count > 1:
                            selected_count = selected_count - 1
                    if btn_plus and btn_plus.collidepoint(event.pos):
                        if selected_pile >= 0 and selected_count < piles[selected_pile]:
                            selected_count = selected_count + 1
                    if btn_jouer and btn_jouer.collidepoint(event.pos):
                        if is_valid(selected_pile, selected_count):
                            apply_move(selected_pile, selected_count)
                            if is_game_over():
                                winner   = current
                                duration = int(time.time() - start_time)
                                save_game(player1, player2, winner, mode, level, duration, DEFAULT_PILES)
                                state = 'win'
                            else:
                                turn          = turn + 1
                                selected_pile  = -1
                                selected_count = 1
                                msg            = ''
                        else:
                            msg       = 'coup invalide !'
                            msg_color = RED
                    if btn_quit and btn_quit.collidepoint(event.pos):
                        state = 'menu'

        # ======= WIN =======
        elif state == 'win':
            btn1, btn2 = draw_win(screen)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if btn1.collidepoint(event.pos):
                        start_game()
                        state = 'game'
                    if btn2.collidepoint(event.pos):
                        state = 'menu'

        # ======= STATS =======
        elif state == 'stats':
            btn1 = draw_stats(screen)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if btn1.collidepoint(event.pos):
                        state = 'menu'

        pygame.display.flip()

if __name__ == '__main__':
    main()
