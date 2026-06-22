import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import time
import winsound
import os

from settings import DEFAULT_PILES, LEVEL_NAMES, MODE_JCJ, MODE_JCIA
from database import create_tables, save_game, get_ranking, get_all_players, insert_player, get_stats, get_full_history, delete_player
from player import create_player
from enemy import get_ai_move

# Configuration globale de CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ============================================================
# PALETTE "DARK MODE" PREMIUM
# ============================================================
BG_NAVBAR  = "#0f172a"
BG_CONTENT = "#1e293b"
TEXT       = "#f8fafc"
TEXT_MUTED = "#94a3b8"
ACCENT     = "#6366f1"
ACCENT_HOVER= "#4f46e5"
DANGER     = "#f43f5e"
CARD_BG    = "#334155"
GREEN      = "#10b981"
BORDER     = "#475569"

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
    global piles, turn, selected_pile, selected_count, start_time, winner
    piles          = list(DEFAULT_PILES)
    turn           = 0
    selected_pile  = -1
    selected_count = 1
    start_time     = time.time()
    winner         = ''

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
    center.place(relx=0.5, rely=0.45, anchor="center")
    
    ctk.CTkLabel(center, text="Jeu de Nim", text_color=TEXT, font=ctk.CTkFont(family=FONT_MAIN, size=50, weight="bold")).pack(pady=10)
    ctk.CTkLabel(center, text="Le classique de la stratégie mathématique.", text_color=TEXT_MUTED, font=ctk.CTkFont(family=FONT_MAIN, size=18)).pack(pady=5)
    
    ctk.CTkLabel(center, text="Le but est de retirer des objets d'une pile à chaque tour.\nCelui qui retire le dernier objet a gagné la partie.", 
                 text_color=TEXT_MUTED, font=ctk.CTkFont(family=FONT_MAIN, size=14), justify="center").pack(pady=40)
             
    actions = ctk.CTkFrame(center, fg_color="transparent")
    actions.pack(pady=20)
    
    ctk.CTkButton(actions, text="Jouer maintenant", fg_color=ACCENT, hover_color=ACCENT_HOVER, text_color="#ffffff", 
                  font=ctk.CTkFont(family=FONT_MAIN, size=16, weight="bold"), width=200, height=50, corner_radius=10, 
                  cursor="hand2", command=show_jouer).pack(side="left", padx=15)
                  
    ctk.CTkButton(actions, text="Gérer les profils", fg_color=CARD_BG, hover_color=BORDER, text_color=TEXT, 
                  font=ctk.CTkFont(family=FONT_MAIN, size=16, weight="bold"), width=200, height=50, corner_radius=10, 
                  border_width=1, border_color=BORDER, cursor="hand2", command=show_profils).pack(side="left", padx=15)

# ============================================================
# ECRAN : PROFILS
# ============================================================
def show_profils():
    update_nav('profils')
    clear_content()
    
    ctk.CTkLabel(content_frame, text="Gestion des Profils", text_color=TEXT, font=ctk.CTkFont(family=FONT_MAIN, size=28, weight="bold"), anchor="w").pack(pady=30, padx=40, fill="x")
    
    # --- Formulaire Création ---
    form_frame = ctk.CTkFrame(content_frame, fg_color=CARD_BG, corner_radius=15, border_width=1, border_color=BORDER)
    form_frame.pack(fill="x", padx=40, pady=10)
    
    # Ajout du padding via les enfants
    ctk.CTkLabel(form_frame, text="Nouveau profil", text_color=TEXT, font=ctk.CTkFont(family=FONT_MAIN, size=16, weight="bold"), anchor="w", justify="left").pack(pady=(20, 15), padx=30, fill="x")
    
    input_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
    input_frame.pack(fill="x", padx=30, pady=(0, 20))
    
    entry = ctk.CTkEntry(input_frame, font=ctk.CTkFont(family=FONT_MAIN, size=14), fg_color=BG_CONTENT, text_color=TEXT, border_color=BORDER, corner_radius=8, height=40, justify="center")
    entry.pack(side="left", fill="x", expand=True)
    
    def add_profil():
        name = entry.get().strip()
        if name:
            create_player(name)
            show_profils()
            
    ctk.CTkButton(input_frame, text="Créer", fg_color=ACCENT, hover_color=ACCENT_HOVER, text_color="#ffffff", 
                  font=ctk.CTkFont(family=FONT_MAIN, size=14, weight="bold"), corner_radius=8, width=100, height=40, 
                  cursor="hand2", command=add_profil).pack(side="left", padx=15)
    
    # --- Liste Joueurs ---
    list_frame = ctk.CTkFrame(content_frame, fg_color=CARD_BG, corner_radius=15, border_width=1, border_color=BORDER)
    list_frame.pack(fill="both", expand=True, padx=40, pady=20)
    
    ctk.CTkLabel(list_frame, text="Joueurs enregistrés", text_color=TEXT, font=ctk.CTkFont(family=FONT_MAIN, size=16, weight="bold"), anchor="w", justify="left").pack(pady=(20, 15), padx=30, fill="x")
    
    table = ctk.CTkFrame(list_frame, fg_color="transparent")
    table.pack(fill="both", expand=True, padx=30, pady=(0, 20))
    
    table.grid_columnconfigure(0, weight=3) # Nom
    table.grid_columnconfigure(1, weight=1) # Score
    table.grid_columnconfigure(2, weight=1) # Victoires
    table.grid_columnconfigure(3, weight=1) # Défaites
    table.grid_columnconfigure(4, weight=1) # Actions
    
    ctk.CTkLabel(table, text="NOM", text_color=TEXT_MUTED, font=ctk.CTkFont(family=FONT_MAIN, size=12, weight="bold"), anchor="w", justify="left").grid(row=0, column=0, sticky="w", pady=5)
    ctk.CTkLabel(table, text="SCORE", text_color=TEXT_MUTED, font=ctk.CTkFont(family=FONT_MAIN, size=12, weight="bold")).grid(row=0, column=1, pady=5)
    ctk.CTkLabel(table, text="VICTOIRES", text_color=TEXT_MUTED, font=ctk.CTkFont(family=FONT_MAIN, size=12, weight="bold")).grid(row=0, column=2, pady=5)
    ctk.CTkLabel(table, text="DÉFAITES", text_color=TEXT_MUTED, font=ctk.CTkFont(family=FONT_MAIN, size=12, weight="bold")).grid(row=0, column=3, pady=5)
    ctk.CTkLabel(table, text="ACTIONS", text_color=TEXT_MUTED, font=ctk.CTkFont(family=FONT_MAIN, size=12, weight="bold")).grid(row=0, column=4, pady=5)
    
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
        p_name = p[1]
        p_wins = p[2]
        p_losses = p[3]
        p_score = p[4]
        
        row_idx = i + 2
        
        ctk.CTkLabel(table, text=p_name, text_color=TEXT, font=ctk.CTkFont(family=FONT_MAIN, size=14, weight="bold"), anchor="w", justify="left").grid(row=row_idx, column=0, sticky="w", pady=5)
        ctk.CTkLabel(table, text=str(p_score), text_color=TEXT, font=ctk.CTkFont(family=FONT_MAIN, size=14)).grid(row=row_idx, column=1, pady=5)
        ctk.CTkLabel(table, text=str(p_wins), text_color=TEXT, font=ctk.CTkFont(family=FONT_MAIN, size=14)).grid(row=row_idx, column=2, pady=5)
        ctk.CTkLabel(table, text=str(p_losses), text_color=TEXT, font=ctk.CTkFont(family=FONT_MAIN, size=14)).grid(row=row_idx, column=3, pady=5)
        
        acts = ctk.CTkFrame(table, fg_color="transparent")
        acts.grid(row=row_idx, column=4, pady=5)
        
        ctk.CTkButton(acts, text="Stats", fg_color=BG_CONTENT, hover_color=BORDER, text_color=TEXT, corner_radius=6, 
                      width=60, height=30, font=ctk.CTkFont(family=FONT_MAIN, size=12, weight="bold"), cursor="hand2",
                      command=lambda n=p_name: force_stats(n)).pack(side="left", padx=5)
                      
        ctk.CTkButton(acts, text="❌", fg_color=DANGER, hover_color="#be123c", text_color="white", corner_radius=6, 
                      width=40, height=30, font=ctk.CTkFont(family=FONT_MAIN, size=12), cursor="hand2",
                      command=lambda n=p_name: del_profil(n)).pack(side="left")

# ============================================================
# ECRAN : STATISTIQUES GLOBAL / JOUEUR
# ============================================================
def show_statistiques():
    global current_stat_player
    clear_content()
    update_nav('statistiques')
    
    head_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
    head_frame.pack(fill="x", pady=30, padx=40)
    
    ctk.CTkLabel(head_frame, text="Statistiques", text_color=TEXT, font=ctk.CTkFont(family=FONT_MAIN, size=28, weight="bold"), anchor="w").pack(side="left")
    
    players = get_all_players()
    if not players:
        ctk.CTkLabel(content_frame, text="Aucun profil enregistré.", text_color=TEXT_MUTED, font=ctk.CTkFont(family=FONT_MAIN, size=18)).pack(pady=100)
        return
        
    names = [p[1] for p in players]
    if current_stat_player not in names:
        current_stat_player = names[0]
        
    def on_change(choice):
        global current_stat_player
        current_stat_player = choice
        show_statistiques()
        
    opt = ctk.CTkOptionMenu(head_frame, values=names, command=on_change, font=ctk.CTkFont(family=FONT_MAIN, size=14), fg_color=CARD_BG, button_color=ACCENT, button_hover_color=ACCENT_HOVER, corner_radius=8, width=200)
    opt.set(current_stat_player)
    opt.pack(side="right")
    
    res = get_stats(current_stat_player)
    if not res: return
    wins, losses, score = res
    total = wins + losses
    taux = (wins / total * 100) if total > 0 else 0.0
    
    # Cards
    cards_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
    cards_frame.pack(pady=10, padx=30, fill="x")
    
    create_card(cards_frame, "SCORE", score, ACCENT).pack(side="left", padx=10, expand=True)
    create_card(cards_frame, "VICTOIRES", wins, GREEN).pack(side="left", padx=10, expand=True)
    create_card(cards_frame, "DÉFAITES", losses, DANGER).pack(side="left", padx=10, expand=True)
    create_card(cards_frame, "TAUX %", f"{taux:.1f}%", TEXT).pack(side="left", padx=10, expand=True)
    
    # Historique
    hist_frame = ctk.CTkFrame(content_frame, fg_color=CARD_BG, corner_radius=15, border_width=1, border_color=BORDER)
    hist_frame.pack(fill="both", expand=True, padx=40, pady=20)
    
    ctk.CTkLabel(hist_frame, text="Dernières parties", text_color=TEXT, font=ctk.CTkFont(family=FONT_MAIN, size=16, weight="bold"), anchor="w", justify="left").pack(pady=(20, 15), padx=30, fill="x")
    
    history = get_full_history(current_stat_player)
    if not history:
        ctk.CTkLabel(hist_frame, text="Aucune partie jouée.", text_color=TEXT_MUTED, font=ctk.CTkFont(family=FONT_MAIN, size=14)).pack(pady=20)
    else:
        table = ctk.CTkFrame(hist_frame, fg_color="transparent")
        table.pack(fill="both", expand=True, padx=30, pady=(0, 20))
        table.grid_columnconfigure(0, weight=1)
        table.grid_columnconfigure(1, weight=2)
        table.grid_columnconfigure(2, weight=2)
        table.grid_columnconfigure(3, weight=1)
        table.grid_columnconfigure(4, weight=1)
        
        for i, row in enumerate(history):
            winn, p1, p2, p_piles, dur, date_g = row
            is_win = (winn == current_stat_player)
            opponent = p2 if p1 == current_stat_player else p1
            
            ctk.CTkLabel(table, text="Victoire" if is_win else "Défaite", text_color=GREEN if is_win else DANGER, anchor="w", justify="left", font=ctk.CTkFont(family=FONT_MAIN, size=13, weight="bold")).grid(row=i*2, column=0, sticky="w", pady=5)
            ctk.CTkLabel(table, text=f"vs {opponent}", text_color=TEXT, anchor="w", justify="left", font=ctk.CTkFont(family=FONT_MAIN, size=13)).grid(row=i*2, column=1, sticky="w", pady=5)
            ctk.CTkLabel(table, text=f"Piles {p_piles}", text_color=TEXT, anchor="w", justify="left", font=ctk.CTkFont(family=FONT_MAIN, size=13)).grid(row=i*2, column=2, sticky="w", pady=5)
            ctk.CTkLabel(table, text=f"{dur}s", text_color=TEXT_MUTED, anchor="e", font=ctk.CTkFont(family=FONT_MAIN, size=13)).grid(row=i*2, column=3, sticky="e", pady=5)
            
            date_str = date_g.strftime("%Y-%m-%d") if date_g else ""
            ctk.CTkLabel(table, text=date_str, text_color=TEXT_MUTED, anchor="e", font=ctk.CTkFont(family=FONT_MAIN, size=12)).grid(row=i*2, column=4, sticky="e", pady=5)
            
            ctk.CTkFrame(table, fg_color=BORDER, height=1).grid(row=i*2+1, column=0, columnspan=5, sticky="we", pady=5)

# ============================================================
# ECRAN : CLASSEMENT GLOBAL
# ============================================================
def show_classement():
    update_nav('classement')
    clear_content()
    
    ctk.CTkLabel(content_frame, text="Classement Global", text_color=TEXT, font=ctk.CTkFont(family=FONT_MAIN, size=28, weight="bold"), anchor="w", justify="left").pack(pady=30, padx=40, fill="x")
    
    list_frame = ctk.CTkFrame(content_frame, fg_color=CARD_BG, corner_radius=15, border_width=1, border_color=BORDER)
    list_frame.pack(fill="both", expand=True, padx=40, pady=20)
    
    table = ctk.CTkFrame(list_frame, fg_color="transparent")
    table.pack(fill="both", expand=True, padx=30, pady=30)
    table.grid_columnconfigure(0, weight=1)
    table.grid_columnconfigure(1, weight=4)
    table.grid_columnconfigure(2, weight=2)
    table.grid_columnconfigure(3, weight=2)
    
    ctk.CTkLabel(table, text="#", text_color=TEXT_MUTED, anchor="w", justify="left", font=ctk.CTkFont(family=FONT_MAIN, size=12, weight="bold")).grid(row=0, column=0, sticky="w", pady=5)
    ctk.CTkLabel(table, text="JOUEUR", text_color=TEXT_MUTED, anchor="w", justify="left", font=ctk.CTkFont(family=FONT_MAIN, size=12, weight="bold")).grid(row=0, column=1, sticky="w", pady=5)
    ctk.CTkLabel(table, text="VICTOIRES", text_color=TEXT_MUTED, anchor="w", justify="left", font=ctk.CTkFont(family=FONT_MAIN, size=12, weight="bold")).grid(row=0, column=2, sticky="w", pady=5)
    ctk.CTkLabel(table, text="SCORE", text_color=TEXT_MUTED, anchor="w", justify="left", font=ctk.CTkFont(family=FONT_MAIN, size=12, weight="bold")).grid(row=0, column=3, sticky="w", pady=5)
    
    ctk.CTkFrame(table, fg_color=BORDER, height=1).grid(row=1, column=0, columnspan=4, sticky="we", pady=10)
    
    results = get_ranking()
    for i, (name, wins, score) in enumerate(results):
        col = ACCENT if i == 0 else TEXT
        
        ctk.CTkLabel(table, text=str(i+1), text_color=col, anchor="w", justify="left", font=ctk.CTkFont(family=FONT_MAIN, size=16, weight="bold")).grid(row=i+2, column=0, sticky="w", pady=8)
        ctk.CTkLabel(table, text=name, text_color=col, anchor="w", justify="left", font=ctk.CTkFont(family=FONT_MAIN, size=16, weight="bold" if i==0 else "normal")).grid(row=i+2, column=1, sticky="w", pady=8)
        ctk.CTkLabel(table, text=str(wins), text_color=TEXT, anchor="w", justify="left", font=ctk.CTkFont(family=FONT_MAIN, size=16)).grid(row=i+2, column=2, sticky="w", pady=8)
        ctk.CTkLabel(table, text=str(score), text_color=ACCENT, anchor="w", justify="left", font=ctk.CTkFont(family=FONT_MAIN, size=16, weight="bold")).grid(row=i+2, column=3, sticky="w", pady=8)

# ============================================================
# ECRAN : JOUER (CONFIGURATION)
# ============================================================
def show_jouer():
    update_nav('jouer')
    clear_content()
    
    ctk.CTkLabel(content_frame, text="Configurer la partie", text_color=TEXT, font=ctk.CTkFont(family=FONT_MAIN, size=28, weight="bold"), anchor="w", justify="left").pack(pady=30, padx=40, fill="x")
    
    # Le conteneur principal
    form = ctk.CTkFrame(content_frame, fg_color=CARD_BG, corner_radius=15, border_width=1, border_color=BORDER)
    form.pack(pady=10, padx=40, fill="x")
    
    # Le sous-conteneur qui va recevoir le padding interne
    inner_form = ctk.CTkFrame(form, fg_color="transparent")
    inner_form.pack(padx=40, pady=40, fill="x")
    
    # Joueur 1
    ctk.CTkLabel(inner_form, text="Joueur 1 :", text_color=TEXT, font=ctk.CTkFont(family=FONT_MAIN, size=16, weight="bold")).grid(row=0, column=0, sticky="w", pady=15)
    e_p1 = ctk.CTkEntry(inner_form, font=ctk.CTkFont(family=FONT_MAIN, size=14), fg_color=BG_CONTENT, text_color=TEXT, border_color=BORDER, width=300, height=45, corner_radius=8, justify="center")
    e_p1.grid(row=0, column=1, padx=30, pady=15)
    
    # Mode
    mode_var = ctk.StringVar(value=MODE_JCIA)
    ctk.CTkLabel(inner_form, text="Adversaire :", text_color=TEXT, font=ctk.CTkFont(family=FONT_MAIN, size=16, weight="bold")).grid(row=1, column=0, sticky="w", pady=15)
    
    radio_frame = ctk.CTkFrame(inner_form, fg_color="transparent")
    radio_frame.grid(row=1, column=1, sticky="w", padx=30)
    
    ctk.CTkRadioButton(radio_frame, text="Ordinateur (IA)", variable=mode_var, value=MODE_JCIA, fg_color=ACCENT, text_color=TEXT, font=ctk.CTkFont(family=FONT_MAIN, size=14), radiobutton_width=22, radiobutton_height=22, hover_color=ACCENT_HOVER, cursor="hand2").pack(side="left")
    ctk.CTkRadioButton(radio_frame, text="Humain (JcJ)", variable=mode_var, value=MODE_JCJ, fg_color=ACCENT, text_color=TEXT, font=ctk.CTkFont(family=FONT_MAIN, size=14), radiobutton_width=22, radiobutton_height=22, hover_color=ACCENT_HOVER, cursor="hand2").pack(side="left", padx=40)
    
    # Joueur 2 / IA Level
    p2_label = ctk.CTkLabel(inner_form, text="Difficulté :", text_color=TEXT, font=ctk.CTkFont(family=FONT_MAIN, size=16, weight="bold"))
    p2_label.grid(row=2, column=0, sticky="w", pady=15)
    
    p2_frame = ctk.CTkFrame(inner_form, fg_color="transparent")
    p2_frame.grid(row=2, column=1, sticky="w", padx=30)
    
    lvl_var = ctk.IntVar(value=1)
    ctk.CTkRadioButton(p2_frame, text="Aléatoire", variable=lvl_var, value=1, fg_color=ACCENT, text_color=TEXT, font=ctk.CTkFont(family=FONT_MAIN, size=13), radiobutton_width=18, radiobutton_height=18).pack(side="left")
    ctk.CTkRadioButton(p2_frame, text="Facile", variable=lvl_var, value=2, fg_color=ACCENT, text_color=TEXT, font=ctk.CTkFont(family=FONT_MAIN, size=13), radiobutton_width=18, radiobutton_height=18).pack(side="left", padx=20)
    ctk.CTkRadioButton(p2_frame, text="Minimax", variable=lvl_var, value=3, fg_color=ACCENT, text_color=TEXT, font=ctk.CTkFont(family=FONT_MAIN, size=13), radiobutton_width=18, radiobutton_height=18).pack(side="left", padx=20)
    ctk.CTkRadioButton(p2_frame, text="Imbattable", variable=lvl_var, value=4, fg_color=ACCENT, text_color=TEXT, font=ctk.CTkFont(family=FONT_MAIN, size=13), radiobutton_width=18, radiobutton_height=18).pack(side="left", padx=20)
    
    e_p2 = ctk.CTkEntry(inner_form, font=ctk.CTkFont(family=FONT_MAIN, size=14), fg_color=BG_CONTENT, text_color=TEXT, border_color=BORDER, width=300, height=45, corner_radius=8, justify="center")
    
    def on_mode_change(*args):
        if mode_var.get() == MODE_JCIA:
            p2_label.configure(text="Difficulté :")
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
            messagebox.showerror("Erreur", "Le nom du Joueur 1 est requis")
            return
            
        m = mode_var.get()
        if m == MODE_JCJ:
            p2 = e_p2.get().strip()
            if not p2:
                messagebox.showerror("Erreur", "Le nom du Joueur 2 est requis")
                return
            player1 = p1
            player2 = p2
            mode = MODE_JCJ
        else:
            player1 = p1
            player2 = 'IA'
            mode = MODE_JCIA
            level = lvl_var.get()
            
        create_player(player1)
        if mode == MODE_JCJ:
            create_player(player2)
            
        start_game()
        show_game()
        
    ctk.CTkButton(inner_form, text="Démarrer la partie", command=launch, fg_color=ACCENT, hover_color=ACCENT_HOVER, text_color="#ffffff", font=ctk.CTkFont(family=FONT_MAIN, size=16, weight="bold"), width=300, height=50, corner_radius=10, cursor="hand2").grid(row=3, column=0, columnspan=2, pady=(40, 0))

# ============================================================
# ECRAN : JEU ACTIF
# ============================================================
def show_game():
    clear_content()
    global canvas, label_msg, btn_minus, btn_plus, btn_jouer, label_info
    
    head = ctk.CTkFrame(content_frame, fg_color="transparent")
    head.pack(fill="x", pady=20, padx=40)
    
    ctk.CTkLabel(head, text=f"{player1} vs {player2}", text_color=TEXT_MUTED, font=ctk.CTkFont(family=FONT_MAIN, size=18, weight="bold")).pack(side="left")
    ctk.CTkButton(head, text="Abandonner", command=show_jouer, fg_color=CARD_BG, hover_color=BORDER, text_color=TEXT, font=ctk.CTkFont(family=FONT_MAIN, size=14, weight="bold"), corner_radius=8, width=120, height=35, border_width=1, border_color=BORDER, cursor="hand2").pack(side="right")
    
    label_info = ctk.CTkLabel(content_frame, text="", text_color=ACCENT, font=ctk.CTkFont(family=FONT_MAIN, size=28, weight="bold"))
    label_info.pack(pady=5)
    
    canvas = tk.Canvas(content_frame, width=700, height=350, bg=BG_CONTENT, highlightthickness=0)
    canvas.pack(pady=20)
    canvas.bind("<Button-1>", canvas_clicked)
    
    control_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
    control_frame.pack(pady=10)
    
    btn_minus = ctk.CTkButton(control_frame, text="−", command=lambda: update_count(-1), font=ctk.CTkFont(family=FONT_MAIN, size=24, weight="bold"), fg_color=CARD_BG, hover_color=BORDER, text_color=TEXT, width=50, height=50, corner_radius=10)
    btn_minus.grid(row=0, column=0, padx=15)
    
    label_msg = ctk.CTkLabel(control_frame, text="Sélectionnez une pile", text_color=TEXT, font=ctk.CTkFont(family=FONT_MAIN, size=16), width=250)
    label_msg.grid(row=0, column=1, padx=10)
    
    btn_plus = ctk.CTkButton(control_frame, text="+", command=lambda: update_count(1), font=ctk.CTkFont(family=FONT_MAIN, size=24, weight="bold"), fg_color=CARD_BG, hover_color=BORDER, text_color=TEXT, width=50, height=50, corner_radius=10)
    btn_plus.grid(row=0, column=2, padx=15)
    
    btn_jouer = ctk.CTkButton(content_frame, text="Confirmer le coup", command=play_human, fg_color=ACCENT, hover_color=ACCENT_HOVER, text_color="#ffffff", font=ctk.CTkFont(family=FONT_MAIN, size=16, weight="bold"), width=250, height=50, corner_radius=10, cursor="hand2")
    btn_jouer.pack(pady=30)
    
    update_game_ui()
    check_turn()

def update_game_ui():
    current = get_current_player()
    label_info.configure(text=f"Tour de : {current}")
    
    canvas.delete("all")
    offset_x = 350 - (len(piles) * 100)
    
    for i in range(len(piles)):
        count = piles[i]
        cx = offset_x + i * 200 + 100
        
        if i == selected_pile:
            canvas.create_rectangle(cx-70, 10, cx+70, 310, outline=ACCENT, width=2, fill=CARD_BG, joinstyle="round")
        else:
            canvas.create_rectangle(cx-70, 10, cx+70, 310, outline=BORDER, width=1, fill=BG_NAVBAR)
            
        for j in range(count):
            cy = 280 - j * 35
            canvas.create_oval(cx-20, cy-15, cx+20, cy+15, fill=ACCENT, outline="", width=0)
            
        col = ACCENT if i == selected_pile else TEXT
        canvas.create_text(cx, 335, text=f"Pile {i+1} ({count})", fill=col, font=(FONT_MAIN, 14, "bold"), justify="center")
        
    if selected_pile >= 0:
        label_msg.configure(text=f"Pile {selected_pile+1} | Retirer : {selected_count}")
        btn_minus.configure(state="normal" if selected_count > 1 else "disabled", fg_color=BORDER if selected_count > 1 else BG_NAVBAR)
        btn_plus.configure(state="normal" if selected_count < piles[selected_pile] else "disabled", fg_color=BORDER if selected_count < piles[selected_pile] else BG_NAVBAR)
        btn_jouer.configure(state="normal", fg_color=ACCENT)
    else:
        label_msg.configure(text="Sélectionnez une pile")
        btn_minus.configure(state="disabled", fg_color=BG_NAVBAR)
        btn_plus.configure(state="disabled", fg_color=BG_NAVBAR)
        btn_jouer.configure(state="disabled", fg_color=BORDER)

def canvas_clicked(event):
    global selected_pile, selected_count
    current = get_current_player()
    if mode == MODE_JCIA and current == 'IA': return
        
    offset_x = 350 - (len(piles) * 100)
    for i in range(len(piles)):
        cx = offset_x + i * 200 + 100
        if cx - 70 <= event.x <= cx + 70 and 10 <= event.y <= 310:
            if piles[i] > 0:
                selected_pile = i
                selected_count = 1
                try:
                    winsound.PlaySound(os.path.join('assets', 'sounds', 'pop.wav'), winsound.SND_ASYNC)
                except: pass
                update_game_ui()

def update_count(delta):
    global selected_count
    if selected_pile >= 0:
        nc = selected_count + delta
        if 1 <= nc <= piles[selected_pile]:
            selected_count = nc
            try:
                winsound.PlaySound(os.path.join('assets', 'sounds', 'pop.wav'), winsound.SND_ASYNC)
            except: pass
            update_game_ui()

def play_human():
    global turn, selected_pile, winner
    if selected_pile >= 0 and 1 <= selected_count <= piles[selected_pile]:
        apply_move(selected_pile, selected_count)
        if is_game_over():
            winner = get_current_player()
            end_game()
        else:
            turn += 1
            selected_pile = -1
            update_game_ui()
            check_turn()

def check_turn():
    current = get_current_player()
    if mode == MODE_JCIA and current == 'IA':
        label_msg.configure(text=f"L'IA réfléchit...")
        btn_jouer.configure(state="disabled", fg_color=BORDER)
        root.update()
        root.after(800, play_ai)

def play_ai():
    global turn, winner
    if is_game_over(): return
    
    pile_index, count = get_ai_move(piles, level)
    apply_move(pile_index, count)
    
    try:
        winsound.PlaySound(os.path.join('assets', 'sounds', 'pop.wav'), winsound.SND_ASYNC)
    except: pass
    
    messagebox.showinfo("Tour de l'IA", f"L'IA a retiré {count} objet(s) de la pile {pile_index+1}")
    
    if is_game_over():
        winner = 'IA'
        end_game()
    else:
        turn += 1
        update_game_ui()

def end_game():
    duration = int(time.time() - start_time)
    save_game(player1, player2, winner, mode, level, duration, DEFAULT_PILES)
    try:
        winsound.PlaySound(os.path.join('assets', 'sounds', 'win.wav'), winsound.SND_ASYNC)
    except: pass
    clear_content()
    
    ctk.CTkLabel(content_frame, text="Partie Terminée", text_color=TEXT_MUTED, font=ctk.CTkFont(family=FONT_MAIN, size=24)).pack(pady=(100, 10))
    ctk.CTkLabel(content_frame, text=f"{winner} a gagné !", text_color=ACCENT, font=ctk.CTkFont(family=FONT_MAIN, size=50, weight="bold")).pack(pady=20)
    
    ctk.CTkButton(content_frame, text="Rejouer", command=show_jouer, fg_color=ACCENT, hover_color=ACCENT_HOVER, text_color="#ffffff", font=ctk.CTkFont(family=FONT_MAIN, size=18, weight="bold"), width=200, height=50, corner_radius=10, cursor="hand2").pack(pady=40)

# ============================================================
# POINT D'ENTREE
# ============================================================
def main():
    global root, content_frame, nav_buttons
    create_tables()
    
    root = ctk.CTk()
    root.title("NimGame - Pro Edition")
    root.geometry("1100x750")
    try:
        root.iconbitmap(os.path.join('assets', 'images', 'icon.ico'))
    except: pass
    
    # Sidebar
    sidebar = ctk.CTkFrame(root, fg_color=BG_NAVBAR, width=250, corner_radius=0)
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)
    
    ctk.CTkLabel(sidebar, text="NimGame.", text_color=ACCENT, font=ctk.CTkFont(family=FONT_MAIN, size=32, weight="bold")).pack(pady=(40, 60))
    
    def create_nav_btn(text, cmd, id_name):
        btn = ctk.CTkButton(sidebar, text=text, fg_color="transparent", text_color=TEXT, font=ctk.CTkFont(family=FONT_MAIN, size=15), 
                            hover_color=CARD_BG, corner_radius=8, anchor="w", width=210, height=45, command=cmd)
        btn.pack(pady=5, padx=20)
        nav_buttons[id_name] = btn
        
    create_nav_btn("Accueil", show_accueil, "accueil")
    create_nav_btn("Jouer", show_jouer, "jouer")
    create_nav_btn("Profils", show_profils, "profils")
    create_nav_btn("Statistiques", show_statistiques, "statistiques")
    create_nav_btn("Classement", show_classement, "classement")
        
    # Content
    content_frame = ctk.CTkFrame(root, fg_color=BG_CONTENT, corner_radius=0)
    content_frame.pack(side="left", fill="both", expand=True)
    
    show_accueil()
    
    root.mainloop()

if __name__ == '__main__':
    main()
