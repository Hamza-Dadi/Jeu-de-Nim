import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import time
import winsound
import os
from PIL import Image

from settings import PILES_DEFAUT as PILES_DEFAUT, NOMS_NIVEAUX as NOMS_NIVEAUX, MODE_JCJ, MODE_JCIA
from database import creer_tables as creer_tables, enregistrer_partie as enregistrer_partie, classement_joueurs as classement_joueurs, lister_joueurs as lister_joueurs, ajouter_joueur as ajouter_joueur, obtenir_statistiques, historique_complet as historique_complet, supprimer_joueur as supprimer_joueur
from player import creer_joueur as creer_joueur
from enemy import jouer_ia as jouer_ia

# Configuration globale de CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Couleurs
FOND_NAVBAR   = "#0f172a"
FOND_CONTENU  = "#1e293b"
TEXTE        = "#f8fafc"
TEXTE_GRIS  = "#94a3b8"
COULEUR_PRINCIPALE      = "#6366f1"
COULEUR_SURVOL= "#4f46e5"
ROUGE_DANGER      = "#f43f5e"
FOND_CARTE     = "#334155"
VERT       = "#10b981"
BORDURE      = "#475569"

POLICE_PRINCIPALE = "Segoe UI"

# ============================================================
# ETAT DU JEU (variables globales)
# ============================================================
piles          = []
joueur1        = ''
joueur2        = ''
mode           = ''
niveau_ia          = 1
tour_actuel           = 0
gagnant         = ''
pile_selectionnee  = -1
nb_selectionne = 1
heure_debut     = 0
ia_en_attente     = False   # garde contre double appel IA

# Variables Interface
fenetre          = None
cadre_contenu = None
toile        = None
texte_message     = None
btn_moins     = None
btn_plus      = None
btn_jouer     = None
texte_info    = None
texte_avatar  = None
boutons_nav   = {}

joueur_stat_actuel = None

AVATARS = ['avatar1.png', 'avatar2.png', 'avatar3.png', 'avatar4.png']
AVATAR_IA = 'avatar3.png'

def get_avatar(nom, taille=48):
    """Retourne l'image avatar d'un joueur selon son nom (ou l'avatar IA)."""
    if nom == 'IA':
        return charger_image(AVATAR_IA, taille, taille)
    joueurs = lister_joueurs()
    noms = [j[1] for j in joueurs]
    idx = noms.index(nom) if nom in noms else 0
    return charger_image(AVATARS[idx % 4], taille, taille)

# ============================================================
# CHARGEMENT DES IMAGES 
# ============================================================
_images_cache = {}
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def charger_image(nom_fichier, largeur, hauteur):
    cle = (nom_fichier, largeur, hauteur)
    if cle in _images_cache:
        return _images_cache[cle]
    chemin = os.path.join(BASE_DIR, 'assets', 'images', nom_fichier)
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
def obtenir_joueur_actuel():
    if mode == MODE_JCJ:
        return joueur1 if tour_actuel % 2 == 0 else joueur2
    return joueur1 if tour_actuel % 2 == 0 else 'IA'

def partie_terminee():
    return sum(piles) == 0

def appliquer_coup(pile_index, count):
    piles[pile_index] -= count

def demarrer_partie():
    global piles, tour_actuel, pile_selectionnee, nb_selectionne, heure_debut, gagnant, ia_en_attente
    piles          = list(PILES_DEFAUT)
    tour_actuel           = 0
    pile_selectionnee  = -1
    nb_selectionne = 1
    heure_debut     = time.time()
    gagnant         = ''
    ia_en_attente     = False

def jouer_son(fichier):
    try:
        chemin_son = os.path.join(BASE_DIR, 'assets', 'sounds', fichier)
        winsound.PlaySound(chemin_son, winsound.SND_ASYNC | winsound.SND_FILENAME)
    except:
        pass

# ============================================================
# UTILS INTERFACE
# ============================================================
def effacer_contenu():
    for widget in cadre_contenu.winfo_children():
        widget.destroy()

def actualiser_navigation(active_name):
    for name, btn in boutons_nav.items():
        if name == active_name:
            btn.configure(fg_color=FOND_CARTE, text_color=COULEUR_PRINCIPALE, font=ctk.CTkFont(family=POLICE_PRINCIPALE, size=15, weight="bold"))
        else:
            btn.configure(fg_color="transparent", text_color=TEXTE, font=ctk.CTkFont(family=POLICE_PRINCIPALE, size=15))

def create_card(parent, title, value, val_color, width=150, height=110):
    card = ctk.CTkFrame(parent, fg_color=FOND_CARTE, width=width, height=height, corner_radius=15, border_width=1, border_color=BORDURE)
    card.pack_propagate(False)
    val_lbl = ctk.CTkLabel(card, text=str(value), text_color=val_color, font=ctk.CTkFont(family=POLICE_PRINCIPALE, size=36, weight="bold"))
    val_lbl.place(relx=0.5, rely=0.45, anchor="center")
    titre_lbl = ctk.CTkLabel(card, text=title, text_color=TEXTE_GRIS, font=ctk.CTkFont(family=POLICE_PRINCIPALE, size=12, weight="bold"))
    titre_lbl.place(relx=0.5, rely=0.85, anchor="center")
    return card

# ============================================================
# ECRAN : ACCUEIL
# ============================================================
def afficher_accueil():
    actualiser_navigation('accueil')
    effacer_contenu()

    center = ctk.CTkFrame(cadre_contenu, fg_color="transparent")
    center.place(relx=0.5, rely=0.47, anchor="center")



    ctk.CTkLabel(center, text="Jeu de Nim", text_color=TEXTE, font=ctk.CTkFont(family=POLICE_PRINCIPALE, size=46, weight="bold")).pack(pady=5)
    ctk.CTkLabel(center, text="Le classique de la strategie mathematique.", text_color=TEXTE_GRIS, font=ctk.CTkFont(family=POLICE_PRINCIPALE, size=16)).pack(pady=4)
    ctk.CTkLabel(center, text="Retirez des objets de vos piles a chaque tour.\nCelui qui retire le dernier objet a gagne la partie.",
                 text_color=TEXTE_GRIS, font=ctk.CTkFont(family=POLICE_PRINCIPALE, size=13), justify="center").pack(pady=20)

    actions = ctk.CTkFrame(center, fg_color="transparent")
    actions.pack(pady=15)

    ctk.CTkButton(actions, text="Jouer maintenant", fg_color=COULEUR_PRINCIPALE, hover_color=COULEUR_SURVOL, text_color="#ffffff",
                  font=ctk.CTkFont(family=POLICE_PRINCIPALE, size=16, weight="bold"), width=200, height=50, corner_radius=10,
                  cursor="hand2", command=show_jouer).pack(side="left", padx=15)
    ctk.CTkButton(actions, text="Gerer les profils", fg_color=FOND_CARTE, hover_color=BORDURE, text_color=TEXTE,
                  font=ctk.CTkFont(family=POLICE_PRINCIPALE, size=16, weight="bold"), width=200, height=50, corner_radius=10,
                  border_width=1, border_color=BORDURE, cursor="hand2", command=show_profils).pack(side="left", padx=15)

# ============================================================
# ECRAN : PROFILS
# ============================================================
def show_profils():
    actualiser_navigation('profils')
    effacer_contenu()

    ctk.CTkLabel(cadre_contenu, text="Gestion des Profils", text_color=TEXTE,
                 font=ctk.CTkFont(family=POLICE_PRINCIPALE, size=28, weight="bold"), anchor="w").pack(pady=30, padx=40, fill="x")

    form_frame = ctk.CTkFrame(cadre_contenu, fg_color=FOND_CARTE, corner_radius=15, border_width=1, border_color=BORDURE)
    form_frame.pack(fill="x", padx=40, pady=10)

    ctk.CTkLabel(form_frame, text="Nouveau profil", text_color=TEXTE,
                 font=ctk.CTkFont(family=POLICE_PRINCIPALE, size=16, weight="bold"), anchor="w").pack(pady=(20, 15), padx=30, fill="x")

    input_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
    input_frame.pack(fill="x", padx=30, pady=(0, 20))

    entry = ctk.CTkEntry(input_frame, font=ctk.CTkFont(family=POLICE_PRINCIPALE, size=14),
                         fg_color=FOND_CONTENU, text_color=TEXTE, border_color=BORDURE, corner_radius=8, height=40, justify="center")
    entry.pack(side="left", fill="x", expand=True)

    def add_profil():
        name = entry.get().strip()
        if not name:
            messagebox.showerror("Erreur", "Le nom ne peut pas etre vide.")
            return
        creer_joueur(name)
        show_profils()

    ctk.CTkButton(input_frame, text="Creer", fg_color=COULEUR_PRINCIPALE, hover_color=COULEUR_SURVOL, text_color="#ffffff",
                  font=ctk.CTkFont(family=POLICE_PRINCIPALE, size=14, weight="bold"), corner_radius=8, width=100, height=40,
                  cursor="hand2", command=add_profil).pack(side="left", padx=15)

    cadre_liste = ctk.CTkFrame(cadre_contenu, fg_color=FOND_CARTE, corner_radius=15, border_width=1, border_color=BORDURE)
    cadre_liste.pack(fill="both", expand=True, padx=40, pady=20)

    ctk.CTkLabel(cadre_liste, text="Joueurs enregistres", text_color=TEXTE,
                 font=ctk.CTkFont(family=POLICE_PRINCIPALE, size=16, weight="bold"), anchor="w").pack(pady=(20, 15), padx=30, fill="x")

    tableau = ctk.CTkFrame(cadre_liste, fg_color="transparent")
    tableau.pack(fill="both", expand=True, padx=30, pady=(0, 20))

    tableau.grid_columnconfigure(0, weight=3)
    tableau.grid_columnconfigure(1, weight=1)
    tableau.grid_columnconfigure(2, weight=1)
    tableau.grid_columnconfigure(3, weight=1)
    tableau.grid_columnconfigure(4, weight=1)

    for col, header in enumerate(["NOM", "SCORE", "VICTOIRES", "DEFAITES", "ACTIONS"]):
        ctk.CTkLabel(tableau, text=header, text_color=TEXTE_GRIS,
                     font=ctk.CTkFont(family=POLICE_PRINCIPALE, size=12, weight="bold"), anchor="w").grid(row=0, column=col, sticky="w", pady=5)

    ctk.CTkFrame(tableau, fg_color=BORDURE, height=1).grid(row=1, column=0, columnspan=5, sticky="we", pady=10)

    def del_profil(name):
        if messagebox.askyesno("Confirmation", f"Supprimer le profil '{name}' ?"):
            supprimer_joueur(name)
            show_profils()

    def force_stats(name):
        global joueur_stat_actuel
        joueur_stat_actuel = name
        show_statistiques()

    players = lister_joueurs()
    for i, p in enumerate(players):
        p_name, p_wins, p_losses, p_score = p[1], p[2], p[3], p[4]
        row_idx = i + 2
        # Avatar + Nom dans la meme cellule
        nom_frame = ctk.CTkFrame(tableau, fg_color="transparent")
        nom_frame.grid(row=row_idx, column=0, sticky="w", pady=5)
        av = get_avatar(p_name, taille=36)
        if av:
            ctk.CTkLabel(nom_frame, image=av, text="").pack(side="left", padx=(0, 8))
        ctk.CTkLabel(nom_frame, text=p_name, text_color=TEXTE,
                     font=ctk.CTkFont(family=POLICE_PRINCIPALE, size=14, weight="bold"), anchor="w").pack(side="left")
        ctk.CTkLabel(tableau, text=str(p_score), text_color=TEXTE,
                     font=ctk.CTkFont(family=POLICE_PRINCIPALE, size=14)).grid(row=row_idx, column=1, pady=5)
        ctk.CTkLabel(tableau, text=str(p_wins), text_color=TEXTE,
                     font=ctk.CTkFont(family=POLICE_PRINCIPALE, size=14)).grid(row=row_idx, column=2, pady=5)
        ctk.CTkLabel(tableau, text=str(p_losses), text_color=TEXTE,
                     font=ctk.CTkFont(family=POLICE_PRINCIPALE, size=14)).grid(row=row_idx, column=3, pady=5)
        acts = ctk.CTkFrame(tableau, fg_color="transparent")
        acts.grid(row=row_idx, column=4, pady=5)
        ctk.CTkButton(acts, text="Stats", fg_color=FOND_CONTENU, hover_color=BORDURE, text_color=TEXTE,
                      corner_radius=6, width=60, height=30, font=ctk.CTkFont(family=POLICE_PRINCIPALE, size=12, weight="bold"),
                      cursor="hand2", command=lambda n=p_name: force_stats(n)).pack(side="left", padx=5)
        ctk.CTkButton(acts, text="X", fg_color=ROUGE_DANGER, hover_color="#be123c", text_color="white",
                      corner_radius=6, width=40, height=30, font=ctk.CTkFont(family=POLICE_PRINCIPALE, size=12),
                      cursor="hand2", command=lambda n=p_name: del_profil(n)).pack(side="left")

# ============================================================
# ECRAN : STATISTIQUES
# ============================================================
def show_statistiques():
    global joueur_stat_actuel
    effacer_contenu()
    actualiser_navigation('statistiques')

    head_frame = ctk.CTkFrame(cadre_contenu, fg_color="transparent")
    head_frame.pack(fill="x", pady=30, padx=40)
    ctk.CTkLabel(head_frame, text="Statistiques", text_color=TEXTE,
                 font=ctk.CTkFont(family=POLICE_PRINCIPALE, size=28, weight="bold"), anchor="w").pack(side="left")

    players = lister_joueurs()
    if not players:
        ctk.CTkLabel(cadre_contenu, text="Aucun profil enregistre.", text_color=TEXTE_GRIS,
                     font=ctk.CTkFont(family=POLICE_PRINCIPALE, size=18)).pack(pady=100)
        return

    names = [p[1] for p in players]
    if joueur_stat_actuel not in names:
        joueur_stat_actuel = names[0]

    def on_change(choice):
        global joueur_stat_actuel
        joueur_stat_actuel = choice
        show_statistiques()

    opt = ctk.CTkOptionMenu(head_frame, values=names, command=on_change,
                            font=ctk.CTkFont(family=POLICE_PRINCIPALE, size=14), fg_color=FOND_CARTE,
                            button_color=COULEUR_PRINCIPALE, button_hover_color=COULEUR_SURVOL, corner_radius=8, width=200)
    opt.set(joueur_stat_actuel)
    opt.pack(side="right")

    # Avatar du joueur selectionne
    av = get_avatar(joueur_stat_actuel, taille=52)
    if av:
        ctk.CTkLabel(head_frame, image=av, text="").pack(side="left", padx=(20, 6))

    res = obtenir_statistiques(joueur_stat_actuel)
    if not res:
        ctk.CTkLabel(cadre_contenu, text="Aucune statistique disponible.", text_color=TEXTE_GRIS,
                     font=ctk.CTkFont(family=POLICE_PRINCIPALE, size=16)).pack(pady=50)
        return

    wins, losses, score = res
    total = wins + losses
    taux = round(wins / total * 100, 1) if total > 0 else 0.0

    cards_frame = ctk.CTkFrame(cadre_contenu, fg_color="transparent")
    cards_frame.pack(pady=10, padx=30, fill="x")
    create_card(cards_frame, "SCORE", score, COULEUR_PRINCIPALE).pack(side="left", padx=10, expand=True)
    create_card(cards_frame, "VICTOIRES", wins, VERT).pack(side="left", padx=10, expand=True)
    create_card(cards_frame, "DEFAITES", losses, ROUGE_DANGER).pack(side="left", padx=10, expand=True)
    create_card(cards_frame, "TAUX %", f"{taux:.1f}%", TEXTE).pack(side="left", padx=10, expand=True)

    hist_frame = ctk.CTkFrame(cadre_contenu, fg_color=FOND_CARTE, corner_radius=15, border_width=1, border_color=BORDURE)
    hist_frame.pack(fill="both", expand=True, padx=40, pady=20)
    ctk.CTkLabel(hist_frame, text="Dernieres parties", text_color=TEXTE,
                 font=ctk.CTkFont(family=POLICE_PRINCIPALE, size=16, weight="bold"), anchor="w").pack(pady=(20, 15), padx=30, fill="x")

    history = historique_complet(joueur_stat_actuel)
    if not history:
        ctk.CTkLabel(hist_frame, text="Aucune partie jouee.", text_color=TEXTE_GRIS,
                     font=ctk.CTkFont(family=POLICE_PRINCIPALE, size=14)).pack(pady=20)
    else:
        tableau = ctk.CTkFrame(hist_frame, fg_color="transparent")
        tableau.pack(fill="both", expand=True, padx=30, pady=(0, 20))
        for col, w in enumerate([1, 2, 2, 1, 1]):
            tableau.grid_columnconfigure(col, weight=w)

        for i, row in enumerate(history):
            gagnant, p1, p2, p_piles, dur, date_g = row
            is_win  = (gagnant == joueur_stat_actuel)
            opponent = p2 if p1 == joueur_stat_actuel else p1

            ctk.CTkLabel(tableau, text="Victoire" if is_win else "Defaite",
                         text_color=VERT if is_win else ROUGE_DANGER, anchor="w",
                         font=ctk.CTkFont(family=POLICE_PRINCIPALE, size=13, weight="bold")).grid(row=i*2, column=0, sticky="w", pady=5)
            ctk.CTkLabel(tableau, text=f"vs {opponent}", text_color=TEXTE, anchor="w",
                         font=ctk.CTkFont(family=POLICE_PRINCIPALE, size=13)).grid(row=i*2, column=1, sticky="w", pady=5)
            ctk.CTkLabel(tableau, text=f"Piles {p_piles}", text_color=TEXTE, anchor="w",
                         font=ctk.CTkFont(family=POLICE_PRINCIPALE, size=13)).grid(row=i*2, column=2, sticky="w", pady=5)
            ctk.CTkLabel(tableau, text=f"{dur}s", text_color=TEXTE_GRIS, anchor="e",
                         font=ctk.CTkFont(family=POLICE_PRINCIPALE, size=13)).grid(row=i*2, column=3, sticky="e", pady=5)
            # Protection si date_g est None ou pas formatable
            try:
                date_str = date_g.strftime("%Y-%m-%d") if date_g else ""
            except:
                date_str = str(date_g) if date_g else ""
            ctk.CTkLabel(tableau, text=date_str, text_color=TEXTE_GRIS, anchor="e",
                         font=ctk.CTkFont(family=POLICE_PRINCIPALE, size=12)).grid(row=i*2, column=4, sticky="e", pady=5)
            ctk.CTkFrame(tableau, fg_color=BORDURE, height=1).grid(row=i*2+1, column=0, columnspan=5, sticky="we", pady=5)

# ============================================================
# ECRAN : CLASSEMENT GLOBAL
# ============================================================
def show_classement():
    actualiser_navigation('classement')
    effacer_contenu()

    ctk.CTkLabel(cadre_contenu, text="Classement Global", text_color=TEXTE,
                 font=ctk.CTkFont(family=POLICE_PRINCIPALE, size=28, weight="bold"), anchor="w").pack(pady=30, padx=40, fill="x")

    cadre_liste = ctk.CTkFrame(cadre_contenu, fg_color=FOND_CARTE, corner_radius=15, border_width=1, border_color=BORDURE)
    cadre_liste.pack(fill="both", expand=True, padx=40, pady=20)

    tableau = ctk.CTkFrame(cadre_liste, fg_color="transparent")
    tableau.pack(fill="both", expand=True, padx=30, pady=30)
    for col, w in enumerate([1, 4, 2, 2]):
        tableau.grid_columnconfigure(col, weight=w)

    for col, header in enumerate(["#", "JOUEUR", "VICTOIRES", "SCORE"]):
        ctk.CTkLabel(tableau, text=header, text_color=TEXTE_GRIS, anchor="w",
                     font=ctk.CTkFont(family=POLICE_PRINCIPALE, size=12, weight="bold")).grid(row=0, column=col, sticky="w", pady=5)

    ctk.CTkFrame(tableau, fg_color=BORDURE, height=1).grid(row=1, column=0, columnspan=4, sticky="we", pady=10)

    results = classement_joueurs()
    for i, (name, wins, score) in enumerate(results):
        col = COULEUR_PRINCIPALE if i == 0 else TEXTE
        ctk.CTkLabel(tableau, text=str(i+1), text_color=col, anchor="w",
                     font=ctk.CTkFont(family=POLICE_PRINCIPALE, size=16, weight="bold")).grid(row=i+2, column=0, sticky="w", pady=8)
        ctk.CTkLabel(tableau, text=name, text_color=col, anchor="w",
                     font=ctk.CTkFont(family=POLICE_PRINCIPALE, size=16, weight="bold" if i == 0 else "normal")).grid(row=i+2, column=1, sticky="w", pady=8)
        ctk.CTkLabel(tableau, text=str(wins), text_color=TEXTE, anchor="w",
                     font=ctk.CTkFont(family=POLICE_PRINCIPALE, size=16)).grid(row=i+2, column=2, sticky="w", pady=8)
        ctk.CTkLabel(tableau, text=str(score), text_color=COULEUR_PRINCIPALE, anchor="w",
                     font=ctk.CTkFont(family=POLICE_PRINCIPALE, size=16, weight="bold")).grid(row=i+2, column=3, sticky="w", pady=8)

# ============================================================
# ECRAN : CONFIGURATION PARTIE
# ============================================================
def show_jouer():
    actualiser_navigation('jouer')
    effacer_contenu()

    ctk.CTkLabel(cadre_contenu, text="Configurer la partie", text_color=TEXTE,
                 font=ctk.CTkFont(family=POLICE_PRINCIPALE, size=28, weight="bold"), anchor="w").pack(pady=30, padx=40, fill="x")

    formulaire = ctk.CTkFrame(cadre_contenu, fg_color=FOND_CARTE, corner_radius=15, border_width=1, border_color=BORDURE)
    formulaire.pack(pady=10, padx=40, fill="x")

    formulaire_interne = ctk.CTkFrame(formulaire, fg_color="transparent")
    formulaire_interne.pack(padx=40, pady=40, fill="x")

    # Liste des profils existants
    players_data = lister_joueurs()
    player_names = [p[1] for p in players_data] if players_data else ["Joueur1"]

    # Joueur 1
    ctk.CTkLabel(formulaire_interne, text="Joueur 1 :", text_color=TEXTE,
                 font=ctk.CTkFont(family=POLICE_PRINCIPALE, size=16, weight="bold")).grid(row=0, column=0, sticky="w", pady=15)
    e_p1 = ctk.CTkComboBox(formulaire_interne, values=player_names, font=ctk.CTkFont(family=POLICE_PRINCIPALE, size=14), fg_color=FOND_CONTENU,
                           text_color=TEXTE, border_color=BORDURE, width=300, height=45, corner_radius=8, justify="center",
                           button_color=COULEUR_PRINCIPALE, button_hover_color=COULEUR_SURVOL)
    e_p1.set("")
    e_p1.grid(row=0, column=1, padx=30, pady=15)

    # Mode
    mode_var = ctk.StringVar(value=MODE_JCIA)
    ctk.CTkLabel(formulaire_interne, text="Adversaire :", text_color=TEXTE,
                 font=ctk.CTkFont(family=POLICE_PRINCIPALE, size=16, weight="bold")).grid(row=1, column=0, sticky="w", pady=15)

    cadre_radio = ctk.CTkFrame(formulaire_interne, fg_color="transparent")
    cadre_radio.grid(row=1, column=1, sticky="w", padx=30)
    ctk.CTkRadioButton(cadre_radio, text="Ordinateur (IA)", variable=mode_var, value=MODE_JCIA,
                       fg_color=COULEUR_PRINCIPALE, text_color=TEXTE, font=ctk.CTkFont(family=POLICE_PRINCIPALE, size=14),
                       radiobutton_width=22, radiobutton_height=22, hover_color=COULEUR_SURVOL, cursor="hand2").pack(side="left")
    ctk.CTkRadioButton(cadre_radio, text="Humain (JcJ)", variable=mode_var, value=MODE_JCJ,
                       fg_color=COULEUR_PRINCIPALE, text_color=TEXTE, font=ctk.CTkFont(family=POLICE_PRINCIPALE, size=14),
                       radiobutton_width=22, radiobutton_height=22, hover_color=COULEUR_SURVOL, cursor="hand2").pack(side="left", padx=40)

    # Niveau IA ou Joueur 2
    p2_label = ctk.CTkLabel(formulaire_interne, text="Difficulte :", text_color=TEXTE,
                             font=ctk.CTkFont(family=POLICE_PRINCIPALE, size=16, weight="bold"))
    p2_label.grid(row=2, column=0, sticky="w", pady=15)

    p2_frame = ctk.CTkFrame(formulaire_interne, fg_color="transparent")
    p2_frame.grid(row=2, column=1, sticky="w", padx=30)

    lvl_var = ctk.IntVar(value=1)
    for txt, val in [("Aleatoire", 1), ("Facile", 2), ("Minimax", 3), ("Imbattable", 4)]:
        ctk.CTkRadioButton(p2_frame, text=txt, variable=lvl_var, value=val, fg_color=COULEUR_PRINCIPALE, text_color=TEXTE,
                           font=ctk.CTkFont(family=POLICE_PRINCIPALE, size=13), radiobutton_width=18,
                           radiobutton_height=18, cursor="hand2").pack(side="left", padx=8)

    player_names_p2 = player_names.copy()
    if len(player_names_p2) == 0: player_names_p2 = ["Joueur2"]

    e_p2 = ctk.CTkComboBox(formulaire_interne, values=player_names_p2, font=ctk.CTkFont(family=POLICE_PRINCIPALE, size=14), fg_color=FOND_CONTENU,
                           text_color=TEXTE, border_color=BORDURE, width=300, height=45, corner_radius=8, justify="center",
                           button_color=COULEUR_PRINCIPALE, button_hover_color=COULEUR_SURVOL)
    e_p2.set("")

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
        global joueur1, joueur2, mode, niveau_ia
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
            joueur1 = p1
            joueur2 = p2
            mode    = MODE_JCJ
        else:
            joueur1 = p1
            joueur2 = 'IA'
            mode    = MODE_JCIA
            niveau_ia   = lvl_var.get()

        creer_joueur(joueur1)
        if mode == MODE_JCJ:
            creer_joueur(joueur2)

        demarrer_partie()
        afficher_jeu()

    ctk.CTkButton(formulaire_interne, text="Demarrer la partie", command=launch, fg_color=COULEUR_PRINCIPALE,
                  hover_color=COULEUR_SURVOL, text_color="#ffffff", font=ctk.CTkFont(family=POLICE_PRINCIPALE, size=16, weight="bold"),
                  width=300, height=50, corner_radius=10, cursor="hand2").grid(row=3, column=0, columnspan=2, pady=(40, 0))

# ============================================================
# ECRAN : JEU ACTIF
# ============================================================
def afficher_jeu():
    effacer_contenu()
    global toile, texte_message, btn_moins, btn_plus, btn_jouer, texte_info, texte_avatar

    entete = ctk.CTkFrame(cadre_contenu, fg_color="transparent")
    entete.pack(fill="x", pady=20, padx=40)
    ctk.CTkLabel(entete, text=f"{joueur1} vs {joueur2}", text_color=TEXTE_GRIS,
                 font=ctk.CTkFont(family=POLICE_PRINCIPALE, size=18, weight="bold")).pack(side="left")
    ctk.CTkButton(entete, text="Abandonner", command=show_jouer, fg_color=FOND_CARTE, hover_color=BORDURE,
                  text_color=TEXTE, font=ctk.CTkFont(family=POLICE_PRINCIPALE, size=14, weight="bold"),
                  corner_radius=8, width=120, height=35, border_width=1, border_color=BORDURE, cursor="hand2").pack(side="right")

    # Zone tour : avatar + label
    tour_frame = ctk.CTkFrame(cadre_contenu, fg_color="transparent")
    tour_frame.pack(pady=5)

    texte_avatar = ctk.CTkLabel(tour_frame, text="", image=None)
    texte_avatar.pack(side="left", padx=(0, 10))

    texte_info = ctk.CTkLabel(tour_frame, text="", text_color=COULEUR_PRINCIPALE,
                              font=ctk.CTkFont(family=POLICE_PRINCIPALE, size=26, weight="bold"))
    texte_info.pack(side="left")

    # Canvas tk standard (pas CTk) pour le dessin des piles
    toile = tk.Canvas(cadre_contenu, width=700, height=380, bg=FOND_CONTENU, highlightthickness=0)
    toile.pack(pady=10)
    toile.bind("<Button-1>", clic_sur_toile)

    cadre_controle = ctk.CTkFrame(cadre_contenu, fg_color="transparent")
    cadre_controle.pack(pady=10)

    btn_moins = ctk.CTkButton(cadre_controle, text="-", command=lambda: modifier_quantite(-1),
                              font=ctk.CTkFont(family=POLICE_PRINCIPALE, size=24, weight="bold"),
                              fg_color=FOND_CARTE, hover_color=BORDURE, text_color=TEXTE, width=50, height=50, corner_radius=10)
    btn_moins.grid(row=0, column=0, padx=15)

    texte_message = ctk.CTkLabel(cadre_controle, text="Selectionnez une pile", text_color=TEXTE,
                             font=ctk.CTkFont(family=POLICE_PRINCIPALE, size=16), width=280)
    texte_message.grid(row=0, column=1, padx=10)

    btn_plus = ctk.CTkButton(cadre_controle, text="+", command=lambda: modifier_quantite(1),
                             font=ctk.CTkFont(family=POLICE_PRINCIPALE, size=24, weight="bold"),
                             fg_color=FOND_CARTE, hover_color=BORDURE, text_color=TEXTE, width=50, height=50, corner_radius=10)
    btn_plus.grid(row=0, column=2, padx=15)

    btn_jouer = ctk.CTkButton(cadre_contenu, text="Confirmer le coup", command=jouer_humain,
                              fg_color=BORDURE, hover_color=COULEUR_SURVOL, text_color="#ffffff",
                              font=ctk.CTkFont(family=POLICE_PRINCIPALE, size=16, weight="bold"),
                              width=250, height=50, corner_radius=10, cursor="hand2", state="disabled")
    btn_jouer.pack(pady=20)

    actualiser_jeu_ui()
    verifier_tour()

# ============================================================
# DESSIN DU JEU
# ============================================================
def actualiser_jeu_ui():
    # Protection : si le toile n'existe plus (page changee), on sort
    if toile is None:
        return
    try:
        toile.winfo_exists()
    except:
        return

    current = obtenir_joueur_actuel()
    if texte_info:
        texte_info.configure(text=f"Tour de : {current}")
    if texte_avatar:
        av = get_avatar(current, taille=44)
        if av:
            texte_avatar.configure(image=av, text="")
        else:
            texte_avatar.configure(image=None, text="")

    toile.delete("all")

    nb_piles = len(piles)
    # Centrage dynamique selon le nombre de piles
    espacement = 200
    total_w    = nb_piles * espacement
    offset_x   = (700 - total_w) // 2 + espacement // 2

    for i in range(nb_piles):
        count = piles[i]
        cx    = offset_x + i * espacement

        # Rectangle de la pile
        if i == pile_selectionnee:
            toile.create_rectangle(cx-70, 10, cx+70, 340, outline=COULEUR_PRINCIPALE, width=2, fill=FOND_CARTE)
        else:
            toile.create_rectangle(cx-70, 10, cx+70, 340, outline=BORDURE, width=1, fill=FOND_NAVBAR)

        # Jetons empiles du bas vers le haut
        for j in range(count):
            cy  = 310 - j * 38
            col = COULEUR_PRINCIPALE if i == pile_selectionnee else VERT
            toile.create_rectangle(cx-18, cy-14, cx+18, cy+14, fill=col, outline="#ffffff", width=1)

        # Etiquette de la pile
        col_txt = COULEUR_PRINCIPALE if i == pile_selectionnee else TEXTE
        toile.create_text(cx, 360, text=f"Pile {i+1}  ({count})", fill=col_txt,
                           font=(POLICE_PRINCIPALE, 13, "bold"), anchor="center")

    # Mise a jour des boutons
    if pile_selectionnee >= 0 and piles[pile_selectionnee] > 0:
        texte_message.configure(text=f"Pile {pile_selectionnee+1}  |  Retirer : {nb_selectionne}")
        btn_moins.configure(state="normal" if nb_selectionne > 1 else "disabled",
                            fg_color=BORDURE if nb_selectionne > 1 else FOND_NAVBAR)
        btn_plus.configure(state="normal" if nb_selectionne < piles[pile_selectionnee] else "disabled",
                           fg_color=BORDURE if nb_selectionne < piles[pile_selectionnee] else FOND_NAVBAR)
        btn_jouer.configure(state="normal", fg_color=COULEUR_PRINCIPALE)
    else:
        texte_message.configure(text="Selectionnez une pile")
        btn_moins.configure(state="disabled", fg_color=FOND_NAVBAR)
        btn_plus.configure(state="disabled", fg_color=FOND_NAVBAR)
        btn_jouer.configure(state="disabled", fg_color=BORDURE)

def clic_sur_toile(event):
    global pile_selectionnee, nb_selectionne
    # Refuser si c'est le tour de l'IA ou si l'IA est en train de jouer
    current = obtenir_joueur_actuel()
    if mode == MODE_JCIA and current == 'IA':
        return
    if ia_en_attente:
        return

    nb_piles  = len(piles)
    espacement = 200
    total_w   = nb_piles * espacement
    offset_x  = (700 - total_w) // 2 + espacement // 2

    for i in range(nb_piles):
        cx = offset_x + i * espacement
        if cx - 70 <= event.x <= cx + 70 and 10 <= event.y <= 340:
            if piles[i] > 0:
                pile_selectionnee  = i
                nb_selectionne = 1
                jouer_son('pop.wav')
                actualiser_jeu_ui()
            return  # on s'arrete apres le premier hit

def modifier_quantite(delta):
    global nb_selectionne
    if pile_selectionnee < 0 or pile_selectionnee >= len(piles):
        return
    nc = nb_selectionne + delta
    if 1 <= nc <= piles[pile_selectionnee]:
        nb_selectionne = nc
        jouer_son('pop.wav')
        actualiser_jeu_ui()

def jouer_humain():
    global tour_actuel, pile_selectionnee, nb_selectionne, gagnant
    if pile_selectionnee < 0 or pile_selectionnee >= len(piles):
        return
    if not (1 <= nb_selectionne <= piles[pile_selectionnee]):
        return
    # Appliquer le coup
    appliquer_coup(pile_selectionnee, nb_selectionne)
    jouer_son('pop.wav')
    pile_selectionnee  = -1
    nb_selectionne = 1
    if partie_terminee():
        gagnant = obtenir_joueur_actuel()
        terminer_partie()
        return
    tour_actuel += 1
    actualiser_jeu_ui()
    verifier_tour()

def verifier_tour():
    global ia_en_attente
    current = obtenir_joueur_actuel()
    if mode == MODE_JCIA and current == 'IA':
        ia_en_attente = True
        if texte_message:
            texte_message.configure(text="L'IA reflechit...")
        if btn_jouer:
            btn_jouer.configure(state="disabled", fg_color=BORDURE)
        # Delai avant le coup IA, sans fenetre.update()
        fenetre.after(900, jouer_ordinateur)

def jouer_ordinateur():
    global tour_actuel, gagnant, ia_en_attente
    ia_en_attente = False
    # Verifier que la partie est encore en cours et la page de jeu est active
    if partie_terminee():
        return
    if toile is None:
        return

    pile_index, count = jouer_ia(piles, niveau_ia)
    appliquer_coup(pile_index, count)
    jouer_son('pop.wav')

    if texte_message:
        texte_message.configure(text=f"IA : pile {pile_index+1}, retire {count} objet(s)")

    if partie_terminee():
        gagnant = 'IA'
        fenetre.after(700, terminer_partie)
    else:
        tour_actuel += 1
        actualiser_jeu_ui()

def terminer_partie():
    global toile, texte_message, btn_moins, btn_plus, btn_jouer, texte_info, texte_avatar, ia_en_attente
    ia_en_attente = False
    # Nullifier les references avant de detruire les widgets
    toile       = None
    texte_message    = None
    btn_moins    = None
    btn_plus     = None
    btn_jouer    = None
    texte_info   = None
    texte_avatar = None

    duration = int(time.time() - heure_debut)
    enregistrer_partie(joueur1, joueur2, gagnant, mode, niveau_ia, duration, PILES_DEFAUT)
    jouer_son('win.wav')
    effacer_contenu()

    ctk.CTkLabel(cadre_contenu, text="Partie Terminee !", text_color=TEXTE_GRIS,
                 font=ctk.CTkFont(family=POLICE_PRINCIPALE, size=22)).pack(pady=(80, 5))
    ctk.CTkLabel(cadre_contenu, text=f"{gagnant} a gagne !", text_color=COULEUR_PRINCIPALE,
                 font=ctk.CTkFont(family=POLICE_PRINCIPALE, size=46, weight="bold")).pack(pady=10)
    ctk.CTkButton(cadre_contenu, text="Rejouer", command=show_jouer, fg_color=COULEUR_PRINCIPALE,
                  hover_color=COULEUR_SURVOL, text_color="#ffffff", font=ctk.CTkFont(family=POLICE_PRINCIPALE, size=18, weight="bold"),
                  width=200, height=50, corner_radius=10, cursor="hand2").pack(pady=30)
    ctk.CTkButton(cadre_contenu, text="Accueil", command=afficher_accueil, fg_color=FOND_CARTE,
                  hover_color=BORDURE, text_color=TEXTE, font=ctk.CTkFont(family=POLICE_PRINCIPALE, size=16, weight="bold"),
                  width=200, height=50, corner_radius=10, cursor="hand2").pack(pady=5)

# ============================================================
# POINT D'ENTREE
# ============================================================
def main():
    global fenetre, cadre_contenu, boutons_nav
    creer_tables()

    fenetre = ctk.CTk()
    fenetre.title("NimGame - Pro Edition")
    fenetre.geometry("1100x750")
    fenetre.minsize(900, 650)
    try:
        fenetre.iconbitmap(os.path.join('assets', 'images', 'icon.ico'))
    except:
        pass

    # Sidebar
    barre_laterale = ctk.CTkFrame(fenetre, fg_color=FOND_NAVBAR, width=250, corner_radius=0)
    barre_laterale.pack(side="left", fill="y")
    barre_laterale.pack_propagate(False)

    ctk.CTkLabel(barre_laterale, text="NimGame.", text_color=COULEUR_PRINCIPALE,
                 font=ctk.CTkFont(family=POLICE_PRINCIPALE, size=32, weight="bold")).pack(pady=(40, 60))

    def create_nav_btn(text, cmd, id_name):
        btn = ctk.CTkButton(barre_laterale, text=text, fg_color="transparent", text_color=TEXTE,
                            font=ctk.CTkFont(family=POLICE_PRINCIPALE, size=15),
                            hover_color=FOND_CARTE, corner_radius=8, anchor="w", width=210, height=45, command=cmd)
        btn.pack(pady=5, padx=20)
        boutons_nav[id_name] = btn

    create_nav_btn("  Accueil",       afficher_accueil,       "accueil")
    create_nav_btn("  Jouer",         show_jouer,         "jouer")
    create_nav_btn("  Profils",       show_profils,       "profils")
    create_nav_btn("  Statistiques",  show_statistiques,  "statistiques")
    create_nav_btn("  Classement",    show_classement,    "classement")

    # Zone de contenu principale
    cadre_contenu = ctk.CTkFrame(fenetre, fg_color=FOND_CONTENU, corner_radius=0)
    cadre_contenu.pack(side="left", fill="both", expand=True)

    afficher_accueil()
    fenetre.mainloop()

if __name__ == '__main__':
    main()
