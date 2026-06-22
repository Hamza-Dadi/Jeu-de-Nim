import pymysql
from settings import BD_HOTE, BD_PORT, BD_UTILISATEUR, BD_MOT_PASSE, BD_NOM

# connexion globale partagee par toutes les fonctions (style dal.py du prof)
connexion = pymysql.Connection(
    host=BD_HOTE,
    port=BD_PORT,
    user=BD_UTILISATEUR,
    password=BD_MOT_PASSE,
    database=BD_NOM,
)

def creer_tables():
    with connexion.cursor() as curseur:
        try:
            curseur.execute('''CREATE TABLE IF NOT EXISTS t_joueur(
                id         INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
                nom        VARCHAR(50),
                victoires  INT DEFAULT 0,
                defaites   INT DEFAULT 0,
                score      INT DEFAULT 0
            )''')
            curseur.execute('''CREATE TABLE IF NOT EXISTS t_partie(
                id          INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
                joueur1     VARCHAR(50),
                joueur2     VARCHAR(50),
                gagnant     VARCHAR(50),
                mode        VARCHAR(10),
                niveau      INT,
                duree       INT,
                piles       VARCHAR(50),
                date_partie DATETIME DEFAULT CURRENT_TIMESTAMP
            )''')
            connexion.commit()
        except pymysql.Error as e:
            print(e)
            connexion.rollback()

def ajouter_joueur(nom):
    with connexion.cursor() as curseur:
        try:
            curseur.execute(
                'INSERT INTO t_joueur(nom) VALUES(%s)', (nom,)
            )
            connexion.commit()
        except pymysql.Error as e:
            print(e)
            connexion.rollback()

def chercher_joueur(nom):
    resultat = None
    with connexion.cursor() as curseur:
        try:
            curseur.execute(
                'SELECT * FROM t_joueur WHERE nom=%s', (nom,)
            )
            resultat = curseur.fetchone()
        except pymysql.Error as e:
            print(e)
            connexion.rollback()
    return resultat

def lister_joueurs():
    resultat = []
    with connexion.cursor() as curseur:
        try:
            curseur.execute('SELECT * FROM t_joueur')
            resultat = curseur.fetchall()
        except pymysql.Error as e:
            print(e)
            connexion.rollback()
    return resultat

def enregistrer_partie(joueur1, joueur2, gagnant, mode, niveau, duree, piles):
    with connexion.cursor() as curseur:
        try:
            curseur.execute(
                'INSERT INTO t_partie(joueur1,joueur2,gagnant,mode,niveau,duree,piles) VALUES(%s,%s,%s,%s,%s,%s,%s)',
                (joueur1, joueur2, gagnant, mode, niveau, duree, str(piles))
            )
            curseur.execute(
                'UPDATE t_joueur SET victoires=victoires+1, score=score+10 WHERE nom=%s', (gagnant,)
            )
            perdant = joueur2 if gagnant == joueur1 else joueur1
            curseur.execute(
                'UPDATE t_joueur SET defaites=defaites+1 WHERE nom=%s', (perdant,)
            )
            connexion.commit()
        except pymysql.Error as e:
            print(e)
            connexion.rollback()

def get_stats(nom):
    resultat = None
    with connexion.cursor() as curseur:
        try:
            curseur.execute(
                'SELECT victoires, defaites, score FROM t_joueur WHERE nom=%s', (nom,)
            )
            resultat = curseur.fetchone()
        except pymysql.Error as e:
            print(e)
            connexion.rollback()
    return resultat

def classement_joueurs():
    resultat = []
    with connexion.cursor() as curseur:
        try:
            curseur.execute(
                'SELECT nom, victoires, score FROM t_joueur ORDER BY score DESC'
            )
            resultat = curseur.fetchall()
        except pymysql.Error as e:
            print(e)
            connexion.rollback()
    return resultat

def duree_moyenne_parties():
    resultat = None
    with connexion.cursor() as curseur:
        try:
            curseur.execute(
                'SELECT AVG(duree) FROM t_partie'
            )
            resultat = curseur.fetchone()
        except pymysql.Error as e:
            print(e)
            connexion.rollback()
    return resultat

def parties_par_niveau():
    resultat = []
    with connexion.cursor() as curseur:
        try:
            curseur.execute(
                'SELECT niveau, COUNT(*) FROM t_partie WHERE mode=%s GROUP BY niveau',
                ('JcIA',)
            )
            resultat = curseur.fetchall()
        except pymysql.Error as e:
            print(e)
            connexion.rollback()
    return resultat

def evolution_score(nom):
    resultat = []
    with connexion.cursor() as curseur:
        try:
            curseur.execute(
                'SELECT date_partie, gagnant FROM t_partie WHERE joueur1=%s OR joueur2=%s ORDER BY date_partie',
                (nom, nom)
            )
            resultat = curseur.fetchall()
        except pymysql.Error as e:
            print(e)
            connexion.rollback()
    return resultat

def historique_complet(nom):
    resultat = []
    with connexion.cursor() as curseur:
        try:
            curseur.execute(
                'SELECT gagnant, joueur1, joueur2, piles, duree, date_partie FROM t_partie WHERE joueur1=%s OR joueur2=%s ORDER BY date_partie DESC LIMIT 10',
                (nom, nom)
            )
            resultat = curseur.fetchall()
        except pymysql.Error as e:
            print(e)
            connexion.rollback()
    return resultat

def supprimer_joueur(nom):
    with connexion.cursor() as curseur:
        try:
            curseur.execute('DELETE FROM t_joueur WHERE nom=%s', (nom,))
            connexion.commit()
        except pymysql.Error as e:
            print(e)
            connexion.rollback()

if __name__ == '__main__':
    creer_tables()
    print('tables creees')
    print(lister_joueurs())
