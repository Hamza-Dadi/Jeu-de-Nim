import pymysql
from settings import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME

connection = pymysql.Connection(
    host=DB_HOST,
    port=DB_PORT,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME,
)

def create_tables():
    with connection.cursor() as cursor:
        try:
            cursor.execute('''CREATE TABLE IF NOT EXISTS t_player(
                id       INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
                name     VARCHAR(50),
                wins     INT DEFAULT 0,
                losses   INT DEFAULT 0,
                score    INT DEFAULT 0
            )''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS t_game(
                id         INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
                player1    VARCHAR(50),
                player2    VARCHAR(50),
                winner     VARCHAR(50),
                mode       VARCHAR(10),
                difficulty INT,
                duration   INT,
                piles      VARCHAR(50),
                date_game  DATETIME DEFAULT CURRENT_TIMESTAMP
            )''')
            connection.commit()
        except pymysql.Error as e:
            print(e)
            connection.rollback()

def insert_player(name):
    with connection.cursor() as cursor:
        try:
            cursor.execute(
                'INSERT INTO t_player(name) VALUES(%s)', (name,)
            )
            connection.commit()
        except pymysql.Error as e:
            print(e)
            connection.rollback()

def get_player(name):
    with connection.cursor() as cursor:
        try:
            cursor.execute(
                'SELECT * FROM t_player WHERE name=%s', (name,)
            )
            results = cursor.fetchone()
        except pymysql.Error as e:
            print(e)
            connection.rollback()
    return results

def get_all_players():
    with connection.cursor() as cursor:
        try:
            cursor.execute('SELECT * FROM t_player')
            results = cursor.fetchall()
        except pymysql.Error as e:
            print(e)
            connection.rollback()
    return results

def save_game(player1, player2, winner, mode, difficulty, duration, piles):
    with connection.cursor() as cursor:
        try:
            cursor.execute(
                'INSERT INTO t_game(player1,player2,winner,mode,difficulty,duration,piles) VALUES(%s,%s,%s,%s,%s,%s,%s)',
                (player1, player2, winner, mode, difficulty, duration, str(piles))
            )
            cursor.execute(
                'UPDATE t_player SET wins=wins+1, score=score+10 WHERE name=%s', (winner,)
            )
            loser = player2 if winner == player1 else player1
            cursor.execute(
                'UPDATE t_player SET losses=losses+1 WHERE name=%s', (loser,)
            )
            connection.commit()
        except pymysql.Error as e:
            print(e)
            connection.rollback()

def get_stats(name):
    with connection.cursor() as cursor:
        try:
            cursor.execute(
                'SELECT wins, losses, score FROM t_player WHERE name=%s', (name,)
            )
            results = cursor.fetchone()
        except pymysql.Error as e:
            print(e)
            connection.rollback()
    return results

def get_ranking():
    with connection.cursor() as cursor:
        try:
            cursor.execute(
                'SELECT name, wins, score FROM t_player ORDER BY score DESC'
            )
            results = cursor.fetchall()
        except pymysql.Error as e:
            print(e)
            connection.rollback()
    return results

def get_avg_duration():
    with connection.cursor() as cursor:
        try:
            cursor.execute(
                'SELECT AVG(duration) FROM t_game'
            )
            results = cursor.fetchone()
        except pymysql.Error as e:
            print(e)
            connection.rollback()
    return results

def get_games_by_difficulty():
    with connection.cursor() as cursor:
        try:
            cursor.execute(
                'SELECT difficulty, COUNT(*) FROM t_game WHERE mode=%s GROUP BY difficulty',
                ('JcIA',)
            )
            results = cursor.fetchall()
        except pymysql.Error as e:
            print(e)
            connection.rollback()
    return results

def get_score_evolution(name):
    with connection.cursor() as cursor:
        try:
            cursor.execute(
                'SELECT date_game, winner FROM t_game WHERE player1=%s OR player2=%s ORDER BY date_game',
                (name, name)
            )
            results = cursor.fetchall()
        except pymysql.Error as e:
            print(e)
            connection.rollback()
    return results

if __name__ == '__main__':
    create_tables()
    print('tables creees')
    print(get_all_players())
