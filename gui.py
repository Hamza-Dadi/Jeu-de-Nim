import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import time
import winsound
import os
from PIL import Image

from settings import PILES_DEFAUT as DEFAULT_PILES, NOMS_NIVEAUX as LEVEL_NAMES, MODE_JCJ, MODE_JCIA
from database import creer_tables as create_tables, enregistrer_partie as save_game, classement_joueurs as get_ranking, lister_joueurs as get_all_players, ajouter_joueur as insert_player, get_stats, historique_complet as get_full_history, supprimer_joueur as delete_player
from player import creer_joueur as create_player
from enemy import jouer_ia as get_ai_move

# Configuration globale de CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ============================================================
# PALETTE "DARK MODE" PREMIUM
# ============================================================
BG_NAVBAR   = "#0f172a"
BG_CONTENT  = "#1e293b"
TEXT        = "#f8fafc"
TEXT_MUTED  = "#94a3b8"
ACCENT      = "#6366f1"
ACCENT_HOVER= "#4f46e5"
DANGER      = "#f43f5e"
CARD_BG     = "#334155"
GREEN       = "#10b981"
BORDER      = "#475569"

FONT_MAIN = "Segoe UI"

# ============================================================
# ETAT DU JEU (variables globales)
# ============================================================
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
ia_pending     = False   # garde contre double appel IA

# Variables Interface
root          = None
content_frame = None
canvas        = None
label_msg     = None
btn_minus     = None
btn_plus      = None
btn_jouer     = None
label_info    = None
nav_buttons   = {}

current_stat_player = None

# ============================================================
# CHARGEMENT DES IMAGES  (avec reference gardee pour eviter GC)
# ============================================================
_images_cache = {}

def charger_image(nom_fichier, largeur, hauteur):
    cle = (nom_fichier, largeur, hauteur)
    if cle in _images_cache:
        return _images_cache[cle]
    chemin = os.path.join('assets', 'images', nom_fichier)
    try:
        img = Image.open(chemin)
        ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(largeur, hauteur))
        _images_cache[cle] = ctk_img
        return ctk_img
    except:
        return None

# ============================================================
# LOGIQUE JEU
# ============================================================
def get_current_player():
    if mode == MODE_JCJ:
        return player1 if turn % 2 == 0 else player2
    return player1 if turn % 2 == 0 else 'IA'

def is_game_over():
    return sum(piles) == 0

def apply_move(pile_index, count):
    piles[pile_index] -= count

def start_game():
    global piles, turn, selected_pile, selected_count, start_time, winner, ia_pending
    piles          = list(DEFAULT_PILES)
    turn           = 0
    selected_pile  = -1
    selected_count = 1
    start_time     = time.time()
    winner         = ''
    ia_pending     = False

def jouer_son(fichier):
    try:
        winsound.PlaySound(os.path.join('assets', 'sounds', fichier), winsound.SND_ASYNC)
    except:
        pass

# ============================================================
# UTILS INTERFACE
# ============================================================
def clear_content():
    for widget in content_frame.winfo_children():
        widget.destroy()

def update_nav(active_name):
    for name, btn in nav_buttons.items():
        if name == active_name:
            btn.configure(fg_color=CARD_BG, text_color=ACCENT, font=ctk.CTkFont(family=FONT_MAIN, size=15, weight="bold"))
        else:
            btn.configure(fg_color="transparent", text_color=TEXT, font=ctk.CTkFont(family=FONT_MAIN, size=15))

def create_card(parent, title, value, val_color, width=150, height=110):
    card = ctk.CTkFrame(parent, fg_color=CARD_BG, width=width, height=height, corner_radius=15, border_width=1, border_color=BORDER)
    card.pack_propagate(False)
    val_lbl = ctk.CTkLabel(card, text=str(value), text_color=val_color, font=ctk.CTkFont(family=FONT_MAIN, size=36, weight="bold"))
    val_lbl.place(relx=0.5, rely=0.45, anchor="center")
    title_lbl = ctk.CTkLabel(card, text=title, text_color=TEXT_MUTED, font=ctk.CTkFont(family=FONT_MAIN, size=12, weight="bold"))
    title_lbl.place(relx=0.5, rely=0.85, anchor="center")
    return card

# ============================================================
# ECRAN : ACCUEIL
# ============================================================
def show_accueil():
    update_nav('accueil')
    clear_content()

    center = ctk.CTkFrame(content_frame, fg_color="transparent")
    center.place(relx=0.5, rely=0.47, anchor="center")

    logo_img = charger_image('logo.png', 220, 180)
    if logo_img:
        lbl_logo = ctk.CTkLabel(center, image=logo_img, text="")
        lbl_logo.pack(pady=(0, 10))

    ctk.CTkLabel(center, text="Jeu de Nim", text_color=TEXT, font=ctk.CTkFont(family=FONT_MAIN, size=46, weight="bold")).pack(pady=5)
    ctk.CTkLabel(center, text="Le classique de la strategie mathematique.", text_color=TEXT_MUTED, font=ctk.CTkFont(family=FONT_MAIN, size=16)).pack(pady=4)
    ctk.CTkLabel(center, text="Retirez des objets de vos piles a chaque tour.\nCelui qui retire le dernier objet a gagne la partie.",
                 text_color=TEXT_MUTED, font=ctk.CTkFont(family=FONT_MAIN, size=13), justify="center").pack(pady=20)

    actions = ctk.CTkFrame(center, fg_color="transparent")
    actions.pack(pady=15)

    ctk.CTkButton(actions, text="Jouer maintenant", fg_color=ACCENT, hover_color=ACCENT_HOVER, text_color="#ffffff",
                  font=ctk.CTkFont(family=FONT_MAIN, size=16, weight="bold"), width=200, height=50, corner_radius=10,
                  cursor="hand2", command=show_jouer).pack(side="left", padx=15)
    ctk.CTkButton(actions, text="Gerer les profils", fg_color=CARD_BG, hover_color=BORDER, text_color=TEXT,
                  font=ctk.CTkFont(family=FONT_MAIN, size=16, weight="bold"), width=200, height=50, corner_radius=10,
                  border_width=1, border_color=BORDER, cursor="hand2", command=show_profils).pack(side="left", padx=15)

# ============================================================
# ECRAN : PROFILS
# ============================================================
def show_profils():
    update_nav('profils')
    clear_content()

    ctk.CTkLabel(content_frame, text="Gestion des Profils", text_color=TEXT,
                 font=ctk.CTkFont(family=FONT_MAIN, size=28, weight="bold"), anchor="w").pack(pady=30, padx=40, fill="x")

    form_frame = ctk.CTkFrame(content_frame, fg_color=CARD_BG, corner_radius=15, border_width=1, border_color=BORDER)
    form_frame.pack(fill="x", padx=40, pady=10)

    ctk.CTkLabel(form_frame, text="Nouveau profil", text_color=TEXT,
                 font=ctk.CTkFont(family=FONT_MAIN, size=16, weight="bold"), anchor="w").pack(pady=(20, 15), padx=30, fill="x")

    input_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
    input_frame.pack(fill="x", padx=30, pady=(0, 20))

    entry = ctk.CTkEntry(input_frame, font=ctk.CTkFont(family=FONT_MAIN, size=14),
                         fg_color=BG_CONTENT, text_color=TEXT, border_color=BORDER, corner_radius=8, height=40, justify="center")
    entry.pack(side="left", fill="x", expand=True)

    def add_profil():
        name = entry.get().strip()
        if not name:
            messagebox.showerror("Erreur", "Le nom ne peut pas etre vide.")
            return
        create_player(name)
        show_profils()

    ctk.CTkButton(input_frame, text="Creer", fg_color=ACCENT, hover_color=ACCENT_HOVER, text_color="#ffffff",
                  font=ctk.CTkFont(family=FONT_MAIN, size=14, weight="bold"), corner_radius=8, width=100, height=40,
                  cursor="hand2", command=add_profil).pack(side="left", padx=15)

    list_frame = ctk.CTkFrame(content_frame, fg_color=CARD_BG, corner_radius=15, border_width=1, border_color=BORDER)
    list_frame.pack(fill="both", expand=True, padx=40, pady=20)

    ctk.CTkLabel(list_frame, text="Joueurs enregistres", text_color=TEXT,
                 font=ctk.CTkFont(family=FONT_MAIN, size=16, weight="bold"), anchor="w").pack(pady=(20, 15), padx=30, fill="x")

    table = ctk.CTkFrame(list_frame, fg_color="transparent")
    table.pack(fill="both", expand=True, padx=30, pady=(0, 20))

    table.grid_columnconfigure(0, weight=3)
    table.grid_columnconfigure(1, weight=1)
    table.grid_columnconfigure(2, weight=1)
    table.grid_columnconfigure(3, weight=1)
    table.grid_columnconfigure(4, weight=1)

    for col, header in enumerate(["NOM", "SCORE", "VICTOIRES", "DEFAITES", "ACTIONS"]):
        ctk.CTkLabel(table, text=header, text_color=TEXT_MUTED,
                     font=ctk.CTkFont(family=FONT_MAIN, size=12, weight="bold"), anchor="w").grid(row=0, column=col, sticky="w", pady=5)

    ctk.CTkFrame(table, fg_color=BORDER, height=1).grid(row=1, column=0, columnspan=5, sticky="we", pady=10)

    def del_profil(name):
        if messagebox.askyesno("Confirmation", f"Supprimer le profil '{name}' ?"):
            delete_player(name)
            show_profils()

    def force_stats(name):
        global current_stat_player
        current_stat_player = name
        show_statistiques()

    players = get_all_players()
    for i, p in enumerate(players):
        p_name, p_wins, p_losses, p_score = p[1], p[2], p[3], p[4]
        row_idx = i + 2
        ctk.CTkLabel(table, text=p_name, text_color=TEXT,
                     font=ctk.CTkFont(family=FONT_MAIN, size=14, weight="bold"), anchor="w").grid(row=row_idx, column=0, sticky="w", pady=5)
        ctk.CTkLabel(table, text=str(p_score), text_color=TEXT,
                     font=ctk.CTkFont(family=FONT_MAIN, size=14)).grid(row=row_idx, column=1, pady=5)
        ctk.CTkLabel(table, text=str(p_wins), text_color=TEXT,
                     font=ctk.CTkFont(family=FONT_MAIN, size=14)).grid(row=row_idx, column=2, pady=5)
        ctk.CTkLabel(table, text=str(p_losses), text_color=TEXT,
                     font=ctk.CTkFont(family=FONT_MAIN, size=14)).grid(row=row_idx, column=3, pady=5)
        acts = ctk.CTkFrame(table, fg_color="transparent")
        acts.grid(row=row_idx, column=4, pady=5)
        ctk.CTkButton(acts, text="Stats", fg_color=BG_CONTENT, hover_color=BORDER, text_color=TEXT,
                      corner_radius=6, width=60, height=30, font=ctk.CTkFont(family=FONT_MAIN, size=12, weight="bold"),
                      cursor="hand2", command=lambda n=p_name: force_stats(n)).pack(side="left", padx=5)
        ctk.CTkButton(acts, text="X", fg_color=DANGER, hover_color="#be123c", text_color="white",
                      corner_radius=6, width=40, height=30, font=ctk.CTkFont(family=FONT_MAIN, size=12),
                      cursor="hand2", command=lambda n=p_name: del_profil(n)).pack(side="left")

# ============================================================
# ECRAN : STATISTIQUES
# ============================================================
def show_statistiques():
    global current_stat_player
    clear_content()
    update_nav('statistiques')

    head_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
    head_frame.pack(fill="x", pady=30, padx=40)
    ctk.CTkLabel(head_frame, text="Statistiques", text_color=TEXT,
                 font=ctk.CTkFont(family=FONT_MAIN, size=28, weight="bold"), anchor="w").pack(side="left")

    players = get_all_players()
    if not players:
        ctk.CTkLabel(content_frame, text="Aucun profil enregistre.", text_color=TEXT_MUTED,
                     font=ctk.CTkFont(family=FONT_MAIN, size=18)).pack(pady=100)
        return

    names = [p[1] for p in players]
    if current_stat_player not in names:
        current_stat_player = names[0]

    def on_change(choice):
        global current_stat_player
        current_stat_player = choice
        show_statistiques()

    opt = ctk.CTkOptionMenu(head_frame, values=names, command=on_change,
                            font=ctk.CTkFont(family=FONT_MAIN, size=14), fg_color=CARD_BG,
                            button_color=ACCENT, button_hover_color=ACCENT_HOVER, corner_radius=8, width=200)
    opt.set(current_stat_player)
    opt.pack(side="right")

    res = get_stats(current_stat_player)
    if not res:
        ctk.CTkLabel(content_frame, text="Aucune statistique disponible.", text_color=TEXT_MUTED,
                     font=ctk.CTkFont(family=FONT_MAIN, size=16)).pack(pady=50)
        return

    wins, losses, score = res
    total = wins + losses
    taux = round(wins / total * 100, 1) if total > 0 else 0.0

    cards_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
    cards_frame.pack(pady=10, padx=30, fill="x")
    create_card(cards_frame, "SCORE", score, ACCENT).pack(side="left", padx=10, expand=True)
    create_card(cards_frame, "VICTOIRES", wins, GREEN).pack(side="left", padx=10, expand=True)
    create_card(cards_frame, "DEFAITES", losses, DANGER).pack(side="left", padx=10, expand=True)
    create_card(cards_frame, "TAUX %", f"{taux:.1f}%", TEXT).pack(side="left", padx=10, expand=True)

    hist_frame = ctk.CTkFrame(content_frame, fg_color=CARD_BG, corner_radius=15, border_width=1, border_color=BORDER)
    hist_frame.pack(fill="both", expand=True, padx=40, pady=20)
    ctk.CTkLabel(hist_frame, text="Dernieres parties", text_color=TEXT,
                 font=ctk.CTkFont(family=FONT_MAIN, size=16, weight="bold"), anchor="w").pack(pady=(20, 15), padx=30, fill="x")

    history = get_full_history(current_stat_player)
    if not history:
        ctk.CTkLabel(hist_frame, text="Aucune partie jouee.", text_color=TEXT_MUTED,
                     font=ctk.CTkFont(family=FONT_MAIN, size=14)).pack(pady=20)
    else:
        table = ctk.CTkFrame(hist_frame, fg_color="transparent")
        table.pack(fill="both", expand=True, padx=30, pady=(0, 20))
        for col, w in enumerate([1, 2, 2, 1, 1]):
            table.grid_columnconfigure(col, weight=w)

        for i, row in enumerate(history):
            gagnant, p1, p2, p_piles, dur, date_g = row
            is_win  = (gagnant == current_stat_player)
            opponent = p2 if p1 == current_stat_player else p1

            ctk.CTkLabel(table, text="Victoire" if is_win else "Defaite",
                         text_color=GREEN if is_win else DANGER, anchor="w",
                         font=ctk.CTkFont(family=FONT_MAIN, size=13, weight="bold")).grid(row=i*2, column=0, sticky="w", pady=5)
            ctk.CTkLabel(table, text=f"vs {opponent}", text_color=TEXT, anchor="w",
                         font=ctk.CTkFont(family=FONT_MAIN, size=13)).grid(row=i*2, column=1, sticky="w", pady=5)
            ctk.CTkLabel(table, text=f"Piles {p_piles}", text_color=TEXT, anchor="w",
                         font=ctk.CTkFont(family=FONT_MAIN, size=13)).grid(row=i*2, column=2, sticky="w", pady=5)
            ctk.CTkLabel(table, text=f"{dur}s", text_color=TEXT_MUTED, anchor="e",
                         font=ctk.CTkFont(family=FONT_MAIN, size=13)).grid(row=i*2, column=3, sticky="e", pady=5)
            # Protection si date_g est None ou pas formatable
            try:
                date_str = date_g.strftime("%Y-%m-%d") if date_g else ""
            except:
                date_str = str(date_g) if date_g else ""
            ctk.CTkLabel(table, text=date_str, text_color=TEXT_MUTED, anchor="e",
                         font=ctk.CTkFont(family=FONT_MAIN, size=12)).grid(row=i*2, column=4, sticky="e", pady=5)
            ctk.CTkFrame(table, fg_color=BORDER, height=1).grid(row=i*2+1, column=0, columnspan=5, sticky="we", pady=5)

# ============================================================
# ECRAN : CLASSEMENT GLOBAL
# ============================================================
def show_classement():
    update_nav('classement')
    clear_content()

    ctk.CTkLabel(content_frame, text="Classement Global", text_color=TEXT,
                 font=ctk.CTkFont(family=FONT_MAIN, size=28, weight="bold"), anchor="w").pack(pady=30, padx=40, fill="x")

    list_frame = ctk.CTkFrame(content_frame, fg_color=CARD_BG, corner_radius=15, border_width=1, border_color=BORDER)
    list_frame.pack(fill="both", expand=True, padx=40, pady=20)

    table = ctk.CTkFrame(list_frame, fg_color="transparent")
    table.pack(fill="both", expand=True, padx=30, pady=30)
    for col, w in enumerate([1, 4, 2, 2]):
        table.grid_columnconfigure(col, weight=w)

    for col, header in enumerate(["#", "JOUEUR", "VICTOIRES", "SCORE"]):
        ctk.CTkLabel(table, text=header, text_color=TEXT_MUTED, anchor="w",
                     font=ctk.CTkFont(family=FONT_MAIN, size=12, weight="bold")).grid(row=0, column=col, sticky="w", pady=5)

    ctk.CTkFrame(table, fg_color=BORDER, height=1).grid(row=1, column=0, columnspan=4, sticky="we", pady=10)

    results = get_ranking()
    for i, (name, wins, score) in enumerate(results):
        col = ACCENT if i == 0 else TEXT
        ctk.CTkLabel(table, text=str(i+1), text_color=col, anchor="w",
                     font=ctk.CTkFont(family=FONT_MAIN, size=16, weight="bold")).grid(row=i+2, column=0, sticky="w", pady=8)
        ctk.CTkLabel(table, text=name, text_color=col, anchor="w",
                     font=ctk.CTkFont(family=FONT_MAIN, size=16, weight="bold" if i == 0 else "normal")).grid(row=i+2, column=1, sticky="w", pady=8)
        ctk.CTkLabel(table, text=str(wins), text_color=TEXT, anchor="w",
                     font=ctk.CTkFont(family=FONT_MAIN, size=16)).grid(row=i+2, column=2, sticky="w", pady=8)
        ctk.CTkLabel(table, text=str(score), text_color=ACCENT, anchor="w",
                     font=ctk.CTkFont(family=FONT_MAIN, size=16, weight="bold")).grid(row=i+2, column=3, sticky="w", pady=8)

# ============================================================
# ECRAN : CONFIGURATION PARTIE
# ============================================================
def show_jouer():
    update_nav('jouer')
    clear_content()

    ctk.CTkLabel(content_frame, text="Configurer la partie", text_color=TEXT,
                 font=ctk.CTkFont(family=FONT_MAIN, size=28, weight="bold"), anchor="w").pack(pady=30, padx=40, fill="x")

    form = ctk.CTkFrame(content_frame, fg_color=CARD_BG, corner_radius=15, border_width=1, border_color=BORDER)
    form.pack(pady=10, padx=40, fill="x")

    inner_form = ctk.CTkFrame(form, fg_color="transparent")
    inner_form.pack(padx=40, pady=40, fill="x")

    # Joueur 1
    ctk.CTkLabel(inner_form, text="Joueur 1 :", text_color=TEXT,
                 font=ctk.CTkFont(family=FONT_MAIN, size=16, weight="bold")).grid(row=0, column=0, sticky="w", pady=15)
    e_p1 = ctk.CTkEntry(inner_form, font=ctk.CTkFont(family=FONT_MAIN, size=14), fg_color=BG_CONTENT,
                         text_color=TEXT, border_color=BORDER, width=300, height=45, corner_radius=8, justify="center")
    e_p1.grid(row=0, column=1, padx=30, pady=15)

    # Mode
    mode_var = ctk.StringVar(value=MODE_JCIA)
    ctk.CTkLabel(inner_form, text="Adversaire :", text_color=TEXT,
                 font=ctk.CTkFont(family=FONT_MAIN, size=16, weight="bold")).grid(row=1, column=0, sticky="w", pady=15)

    radio_frame = ctk.CTkFrame(inner_form, fg_color="transparent")
    radio_frame.grid(row=1, column=1, sticky="w", padx=30)
    ctk.CTkRadioButton(radio_frame, text="Ordinateur (IA)", variable=mode_var, value=MODE_JCIA,
                       fg_color=ACCENT, text_color=TEXT, font=ctk.CTkFont(family=FONT_MAIN, size=14),
                       radiobutton_width=22, radiobutton_height=22, hover_color=ACCENT_HOVER, cursor="hand2").pack(side="left")
    ctk.CTkRadioButton(radio_frame, text="Humain (JcJ)", variable=mode_var, value=MODE_JCJ,
                       fg_color=ACCENT, text_color=TEXT, font=ctk.CTkFont(family=FONT_MAIN, size=14),
                       radiobutton_width=22, radiobutton_height=22, hover_color=ACCENT_HOVER, cursor="hand2").pack(side="left", padx=40)

    # Niveau IA ou Joueur 2
    p2_label = ctk.CTkLabel(inner_form, text="Difficulte :", text_color=TEXT,
                             font=ctk.CTkFont(family=FONT_MAIN, size=16, weight="bold"))
    p2_label.grid(row=2, column=0, sticky="w", pady=15)

    p2_frame = ctk.CTkFrame(inner_form, fg_color="transparent")
    p2_frame.grid(row=2, column=1, sticky="w", padx=30)

    lvl_var = ctk.IntVar(value=1)
    for txt, val in [("Aleatoire", 1), ("Facile", 2), ("Minimax", 3), ("Imbattable", 4)]:
        ctk.CTkRadioButton(p2_frame, text=txt, variable=lvl_var, value=val, fg_color=ACCENT, text_color=TEXT,
                           font=ctk.CTkFont(family=FONT_MAIN, size=13), radiobutton_width=18,
                           radiobutton_height=18, cursor="hand2").pack(side="left", padx=8)

    e_p2 = ctk.CTkEntry(inner_form, font=ctk.CTkFont(family=FONT_MAIN, size=14), fg_color=BG_CONTENT,
                         text_color=TEXT, border_color=BORDER, width=300, height=45, corner_radius=8, justify="center")

    def on_mode_change(*args):
        if mode_var.get() == MODE_JCIA:
            p2_label.configure(text="Difficulte :")
            e_p2.grid_forget()
            p2_frame.grid(row=2, column=1, sticky="w", padx=30)
        else:
            p2_label.configure(text="Joueur 2 :")
            p2_frame.grid_forget()
            e_p2.grid(row=2, column=1, sticky="w", padx=30)

    mode_var.trace("w", on_mode_change)

    def launch():
        global player1, player2, mode, level
        p1 = e_p1.get().strip()
        if not p1:
            messagebox.showerror("Erreur", "Le nom du Joueur 1 est requis.")
            return
        m = mode_var.get()
        if m == MODE_JCJ:
            p2 = e_p2.get().strip()
            if not p2:
                messagebox.showerror("Erreur", "Le nom du Joueur 2 est requis.")
                return
            if p1 == p2:
                messagebox.showerror("Erreur", "Les deux joueurs doivent avoir des noms differents.")
                return
            player1 = p1
            player2 = p2
            mode    = MODE_JCJ
        else:
            player1 = p1
            player2 = 'IA'
            mode    = MODE_JCIA
            level   = lvl_var.get()

        create_player(player1)
        if mode == MODE_JCJ:
            create_player(player2)

        start_game()
        show_game()

    ctk.CTkButton(inner_form, text="Demarrer la partie", command=launch, fg_color=ACCENT,
                  hover_color=ACCENT_HOVER, text_color="#ffffff", font=ctk.CTkFont(family=FONT_MAIN, size=16, weight="bold"),
                  width=300, height=50, corner_radius=10, cursor="hand2").grid(row=3, column=0, columnspan=2, pady=(40, 0))

# ============================================================
# ECRAN : JEU ACTIF
# ============================================================
def show_game():
    clear_content()
    global canvas, label_msg, btn_minus, btn_plus, btn_jouer, label_info

    head = ctk.CTkFrame(content_frame, fg_color="transparent")
    head.pack(fill="x", pady=20, padx=40)
    ctk.CTkLabel(head, text=f"{player1} vs {player2}", text_color=TEXT_MUTED,
                 font=ctk.CTkFont(family=FONT_MAIN, size=18, weight="bold")).pack(side="left")
    ctk.CTkButton(head, text="Abandonner", command=show_jouer, fg_color=CARD_BG, hover_color=BORDER,
                  text_color=TEXT, font=ctk.CTkFont(family=FONT_MAIN, size=14, weight="bold"),
                  corner_radius=8, width=120, height=35, border_width=1, border_color=BORDER, cursor="hand2").pack(side="right")

    label_info = ctk.CTkLabel(content_frame, text="", text_color=ACCENT,
                              font=ctk.CTkFont(family=FONT_MAIN, size=26, weight="bold"))
    label_info.pack(pady=5)

    # Canvas tk standard (pas CTk) pour le dessin des piles
    canvas = tk.Canvas(content_frame, width=700, height=380, bg=BG_CONTENT, highlightthickness=0)
    canvas.pack(pady=10)
    canvas.bind("<Button-1>", canvas_clicked)

    control_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
    control_frame.pack(pady=10)

    btn_minus = ctk.CTkButton(control_frame, text="-", command=lambda: update_count(-1),
                              font=ctk.CTkFont(family=FONT_MAIN, size=24, weight="bold"),
                              fg_color=CARD_BG, hover_color=BORDER, text_color=TEXT, width=50, height=50, corner_radius=10)
    btn_minus.grid(row=0, column=0, padx=15)

    label_msg = ctk.CTkLabel(control_frame, text="Selectionnez une pile", text_color=TEXT,
                             font=ctk.CTkFont(family=FONT_MAIN, size=16), width=280)
    label_msg.grid(row=0, column=1, padx=10)

    btn_plus = ctk.CTkButton(control_frame, text="+", command=lambda: update_count(1),
                             font=ctk.CTkFont(family=FONT_MAIN, size=24, weight="bold"),
                             fg_color=CARD_BG, hover_color=BORDER, text_color=TEXT, width=50, height=50, corner_radius=10)
    btn_plus.grid(row=0, column=2, padx=15)

    btn_jouer = ctk.CTkButton(content_frame, text="Confirmer le coup", command=play_human,
                              fg_color=BORDER, hover_color=ACCENT_HOVER, text_color="#ffffff",
                              font=ctk.CTkFont(family=FONT_MAIN, size=16, weight="bold"),
                              width=250, height=50, corner_radius=10, cursor="hand2", state="disabled")
    btn_jouer.pack(pady=20)

    update_game_ui()
    check_turn()

# ============================================================
# DESSIN DU JEU
# ============================================================
def update_game_ui():
    # Protection : si le canvas n'existe plus (page changee), on sort
    if canvas is None:
        return
    try:
        canvas.winfo_exists()
    except:
        return

    current = get_current_player()
    if label_info:
        label_info.configure(text=f"Tour de : {current}")

    canvas.delete("all")

    nb_piles = len(piles)
    # Centrage dynamique selon le nombre de piles
    espacement = 200
    total_w    = nb_piles * espacement
    offset_x   = (700 - total_w) // 2 + espacement // 2

    for i in range(nb_piles):
        count = piles[i]
        cx    = offset_x + i * espacement

        # Rectangle de la pile
        if i == selected_pile:
            canvas.create_rectangle(cx-70, 10, cx+70, 340, outline=ACCENT, width=2, fill=CARD_BG)
        else:
            canvas.create_rectangle(cx-70, 10, cx+70, 340, outline=BORDER, width=1, fill=BG_NAVBAR)

        # Jetons empiles du bas vers le haut
        for j in range(count):
            cy  = 310 - j * 38
            col = ACCENT if i == selected_pile else GREEN
            canvas.create_oval(cx-18, cy-14, cx+18, cy+14, fill=col, outline="#ffffff", width=1)

        # Etiquette de la pile
        col_txt = ACCENT if i == selected_pile else TEXT
        canvas.create_text(cx, 360, text=f"Pile {i+1}  ({count})", fill=col_txt,
                           font=(FONT_MAIN, 13, "bold"), anchor="center")

    # Mise a jour des boutons
    if selected_pile >= 0 and piles[selected_pile] > 0:
        label_msg.configure(text=f"Pile {selected_pile+1}  |  Retirer : {selected_count}")
        btn_minus.configure(state="normal" if selected_count > 1 else "disabled",
                            fg_color=BORDER if selected_count > 1 else BG_NAVBAR)
        btn_plus.configure(state="normal" if selected_count < piles[selected_pile] else "disabled",
                           fg_color=BORDER if selected_count < piles[selected_pile] else BG_NAVBAR)
        btn_jouer.configure(state="normal", fg_color=ACCENT)
    else:
        label_msg.configure(text="Selectionnez une pile")
        btn_minus.configure(state="disabled", fg_color=BG_NAVBAR)
        btn_plus.configure(state="disabled", fg_color=BG_NAVBAR)
        btn_jouer.configure(state="disabled", fg_color=BORDER)

def canvas_clicked(event):
    global selected_pile, selected_count
    # Refuser si c'est le tour de l'IA ou si l'IA est en train de jouer
    current = get_current_player()
    if mode == MODE_JCIA and current == 'IA':
        return
    if ia_pending:
        return

    nb_piles  = len(piles)
    espacement = 200
    total_w   = nb_piles * espacement
    offset_x  = (700 - total_w) // 2 + espacement // 2

    for i in range(nb_piles):
        cx = offset_x + i * espacement
        if cx - 70 <= event.x <= cx + 70 and 10 <= event.y <= 340:
            if piles[i] > 0:
                selected_pile  = i
                selected_count = 1
                jouer_son('pop.wav')
                update_game_ui()
            return  # on s'arrete apres le premier hit

def update_count(delta):
    global selected_count
    if selected_pile < 0 or selected_pile >= len(piles):
        return
    nc = selected_count + delta
    if 1 <= nc <= piles[selected_pile]:
        selected_count = nc
        jouer_son('pop.wav')
        update_game_ui()

def play_human():
    global turn, selected_pile, selected_count, winner
    if selected_pile < 0 or selected_pile >= len(piles):
        return
    if not (1 <= selected_count <= piles[selected_pile]):
        return
    # Appliquer le coup
    apply_move(selected_pile, selected_count)
    jouer_son('pop.wav')
    selected_pile  = -1
    selected_count = 1
    if is_game_over():
        winner = get_current_player()
        end_game()
        return
    turn += 1
    update_game_ui()
    check_turn()

def check_turn():
    global ia_pending
    current = get_current_player()
    if mode == MODE_JCIA and current == 'IA':
        ia_pending = True
        if label_msg:
            label_msg.configure(text="L'IA reflechit...")
        if btn_jouer:
            btn_jouer.configure(state="disabled", fg_color=BORDER)
        # Delai avant le coup IA, sans root.update()
        root.after(900, play_ai)

def play_ai():
    global turn, winner, ia_pending
    ia_pending = False
    # Verifier que la partie est encore en cours et la page de jeu est active
    if is_game_over():
        return
    if canvas is None:
        return

    pile_index, count = get_ai_move(piles, level)
    apply_move(pile_index, count)
    jouer_son('pop.wav')

    if label_msg:
        label_msg.configure(text=f"IA : pile {pile_index+1}, retire {count} objet(s)")

    if is_game_over():
        winner = 'IA'
        root.after(700, end_game)
    else:
        turn += 1
        update_game_ui()

def end_game():
    global canvas, label_msg, btn_minus, btn_plus, btn_jouer, label_info, ia_pending
    ia_pending = False
    # Nullifier les references avant de detruire les widgets
    canvas    = None
    label_msg = None
    btn_minus = None
    btn_plus  = None
    btn_jouer = None
    label_info= None

    duration = int(time.time() - start_time)
    save_game(player1, player2, winner, mode, level, duration, DEFAULT_PILES)
    jouer_son('win.wav')
    clear_content()

    victoire_img = charger_image('victoire.png', 200, 160)
    if victoire_img:
        ctk.CTkLabel(content_frame, image=victoire_img, text="").pack(pady=(40, 5))
    else:
        ctk.CTkLabel(content_frame, text="Victoire !", font=ctk.CTkFont(family=FONT_MAIN, size=48, weight="bold"),
                     text_color=ACCENT).pack(pady=(60, 5))

    ctk.CTkLabel(content_frame, text="Partie Terminee !", text_color=TEXT_MUTED,
                 font=ctk.CTkFont(family=FONT_MAIN, size=22)).pack(pady=(5, 5))
    ctk.CTkLabel(content_frame, text=f"{winner} a gagne !", text_color=ACCENT,
                 font=ctk.CTkFont(family=FONT_MAIN, size=46, weight="bold")).pack(pady=10)
    ctk.CTkButton(content_frame, text="Rejouer", command=show_jouer, fg_color=ACCENT,
                  hover_color=ACCENT_HOVER, text_color="#ffffff", font=ctk.CTkFont(family=FONT_MAIN, size=18, weight="bold"),
                  width=200, height=50, corner_radius=10, cursor="hand2").pack(pady=30)
    ctk.CTkButton(content_frame, text="Accueil", command=show_accueil, fg_color=CARD_BG,
                  hover_color=BORDER, text_color=TEXT, font=ctk.CTkFont(family=FONT_MAIN, size=16, weight="bold"),
                  width=200, height=50, corner_radius=10, cursor="hand2").pack(pady=5)

# ============================================================
# POINT D'ENTREE
# ============================================================
def main():
    global root, content_frame, nav_buttons
    create_tables()

    root = ctk.CTk()
    root.title("NimGame - Pro Edition")
    root.geometry("1100x750")
    root.minsize(900, 650)
    try:
        root.iconbitmap(os.path.join('assets', 'images', 'icon.ico'))
    except:
        pass

    # Sidebar
    sidebar = ctk.CTkFrame(root, fg_color=BG_NAVBAR, width=250, corner_radius=0)
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)

    ctk.CTkLabel(sidebar, text="NimGame.", text_color=ACCENT,
                 font=ctk.CTkFont(family=FONT_MAIN, size=32, weight="bold")).pack(pady=(40, 60))

    def create_nav_btn(text, cmd, id_name):
        btn = ctk.CTkButton(sidebar, text=text, fg_color="transparent", text_color=TEXT,
                            font=ctk.CTkFont(family=FONT_MAIN, size=15),
                            hover_color=CARD_BG, corner_radius=8, anchor="w", width=210, height=45, command=cmd)
        btn.pack(pady=5, padx=20)
        nav_buttons[id_name] = btn

    create_nav_btn("  Accueil",       show_accueil,       "accueil")
    create_nav_btn("  Jouer",         show_jouer,         "jouer")
    create_nav_btn("  Profils",       show_profils,       "profils")
    create_nav_btn("  Statistiques",  show_statistiques,  "statistiques")
    create_nav_btn("  Classement",    show_classement,    "classement")

    # Zone de contenu principale
    content_frame = ctk.CTkFrame(root, fg_color=BG_CONTENT, corner_radius=0)
    content_frame.pack(side="left", fill="both", expand=True)

    show_accueil()
    root.mainloop()

if __name__ == '__main__':
    main()
