import psycopg2

from flask import g, request, session

from mathquiz import app, config, SCHEMA_VERSION, question
from mathquiz.question import Question

@app.before_request
def create_database():
    g.database = psycopg2.connect('user=%s password=%s' % (config.database_user, config.database_password))

    # ensure schema versions are equal
    c = g.database.cursor()
    c.execute("SELECT value FROM app_settings WHERE key = 'schema_version'")
    db_schema_version = c.fetchone()[0]
    c.close()

    g.database.commit()

    if str(SCHEMA_VERSION) != db_schema_version:
        raise Exception('Database schema version not the same as app version, UPGRADE')

    #make sure we have a user object in the database for this connection
    create_user()

@app.teardown_request
def close_database(request):
    g.database.commit()
    g.database.close()
    return request

def set_user(mxit_user_id):
    try:
        c = g.database.cursor()
        c.execute('SELECT id, username, difficulty FROM users WHERE mxit_userid = %s LIMIT 1', (str(mxit_user_id), ))
        session['userId'], session['username'], session['difficulty'] = c.fetchone()
        session['difficulty'] = question.Difficulties[session['difficulty']]
        session['version'] = SCHEMA_VERSION
    finally:
        c.close()

def create_user():
    try:
        mxit_user_id = request.headers['X-Mxit-Userid-R']
        mxit_nick = request.headers['X-Mxit-Nick']
    except KeyError:
        mxit_user_id = -1 # development id
        mxit_nick = 'Yasen'
    c = g.database.cursor()
    try:
        c.execute('INSERT INTO users (mxit_userid, username, joined_date) VALUES (%s, %s, NOW())', (mxit_user_id, mxit_nick))
        c.execute('SELECT lastval()')
        session['userId'] = c.fetchone()[0]
        session['difficulty'] = 'easy'
        session['username'] = mxit_nick
        g.database.commit()
    except psycopg2.IntegrityError:
        g.database.rollback()
        # this isn't an error. We just don't check whether we've added this user before
        if 'userId' not in session or ('version' in session and session['version'] != SCHEMA_VERSION):
            set_user(mxit_user_id)
    finally:
        c.close()

    g.database.commit()

def fetch_user_score(user_id, difficulty):
    if isinstance(difficulty, basestring):
        difficulty = question.Difficulties.index(difficulty)

    c = g.database.cursor()
    c.execute('SELECT highscore FROM users_highscores WHERE userid = %s AND difficulty = %s', (user_id, difficulty))
    row = c.fetchone()
    c.close()

    return row[0] if row is not None else 0

def quiz_answer(user_id, quiz_id, question, answer, correct, score):
    c = g.database.cursor()
    c.execute('INSERT INTO quiz_submissions (user_id, quiz_id, question, answer, correct, score) VALUES (%s, %s, %s, %s, %s, %s)', (user_id, quiz_id, str(question), answer, correct, score))
    c.close()

    g.database.commit()

def cumulative_quiz_score(quiz_id):
    c = g.database.cursor()
    c.execute('SELECT sum(score) as total_score FROM quiz_submissions WHERE quiz_id = %s', (quiz_id, ))
    score = c.fetchone()[0]
    c.close()

    return score

def create_quiz(type):
    c = g.database.cursor()
    c.execute('INSERT INTO quiz (type, start_time, end_time, user_id) VALUES (%s, NOW(), NULL, %s)', (type, session['userId']))
    c.execute('SELECT lastval()')
    quiz_id = c.fetchone()[0]

    c.close()

    g.database.commit()

    return quiz_id

def quiz_complete(difficulty, quiz_id, num_correct, num_questions):
    if isinstance(difficulty, basestring):
        difficulty = question.Difficulties.index(difficulty)

    score = cumulative_quiz_score(quiz_id)
    c = g.database.cursor()
    # update quiz score
    c.execute('UPDATE quiz SET end_time = NOW(), num_correct = %s, num_questions = %s, score =  %s WHERE id = %s',
            (num_correct, num_questions, score, quiz_id))
    g.database.commit()
    try:
        # insert high score into table
        c.execute('INSERT INTO users_highscores (userid, difficulty, highscore) VALUES (%s, %s, %s)',
                (session['userId'], difficulty, score))
    except psycopg2.IntegrityError:
        g.database.rollback()
        # update existing high score
        c.execute('UPDATE users_highscores SET highscore = GREATEST(highscore, %s) WHERE userid = %s',
                (score, session['userId']))
    c.close()

    g.database.commit()

    return score

def calculate_streak_length(user_id, cur_quiz_id):
    c = g.database.cursor()
    c.execute('SELECT correct, quiz_id FROM quiz_submissions WHERE user_id = %s ORDER BY submit_time DESC LIMIT 10', (user_id, ))

    streakLength = 0
    for correct, quiz_id in c:
        # streak began or we moved over to the previous quiz
        if not correct or quiz_id != cur_quiz_id:
            break
        streakLength += 1

    c.close()

    return streakLength


def leaderboard(page, difficulty):
    if isinstance(difficulty, basestring):
        difficulty = question.Difficulties.index(difficulty.upper())
    print difficulty
    c = g.database.cursor()

    c.execute('select username, highscore, users.id from users_highscores, users where users_highscores.difficulty=%s and userid=id ORDER BY highscore DESC OFFSET %s LIMIT 10', (difficulty, page*10));
    result = c.fetchall()
    c.close()

    return result

def leaderboard_size(difficulty):
    if isinstance(difficulty, basestring):
        difficulty = question.Difficulties.index(difficulty.upper())

    c = g.database.cursor()

    c.execute('SELECT count(*) FROM users_highscores WHERE highscore > 0 AND difficulty = %s', (difficulty, ))
    size = c.fetchone()[0]
    c.close()

    return size

def username_exists(username):
    c = g.database.cursor()
    c.execute('SELECT count(*) FROM users WHERE username = %s', (username, ))
    count = c.fetchone()[0]
    c.close()

    return count > 0

def fetch_user_rank(user_id, difficulty):
    if isinstance(difficulty, basestring):
        difficulty = question.Difficulties.index(difficulty.upper())

    c = g.database.cursor()
    c.execute('WITH ranks AS (SELECT userid, rank() OVER (ORDER BY highscore DESC) as rank FROM users_highscores WHERE difficulty = %s) SELECT rank FROM ranks WHERE userid = %s LIMIT 1', (difficulty, user_id))
    row = c.fetchone()
    c.close()

    return int(row[0]) if row is not None else row

def fetch_number_users():
    c = g.database.cursor()
    c.execute('SELECT count(id) FROM users')
    count = c.fetchone()[0]
    c.close()

    return count

def set_user_difficulty(user_id, difficulty):
    c = g.database.cursor()
    c.execute('UPDATE users SET difficulty = %s WHERE id = %s', (difficulty, user_id))
    c.close()
    g.database.commit()

def fetch_user_difficulty(user_id):
    c = g.database.cursor()
    c.execute('SELECT difficulty FROM users WHERE id = %s', (user_id, ))
    row = c.fetchone()
    difficulty = question.Difficulties[row[0]]
    c.close()
    return difficulty

def submit_feedback(user_id, feedback):
    c = g.database.cursor()
    c.execute('INSERT INTO feedback (username, userid, feedback) VALUES ((SELECT username FROM users WHERE id = %s), %s, %s)', (user_id, user_id, feedback))
    c.close()

    g.database.commit()

def fetch_user_games_started(user_id):
    c = g.database.cursor()
    c.execute('SELECT count(*) FROM quiz WHERE user_id = %s', (user_id, ))
    count = c.fetchone()[0]
    c.close()

    return count

def fetch_user_games_completed(user_id):
    c = g.database.cursor()
    c.execute('SELECT count(*) FROM quiz WHERE user_id = %s AND end_time IS NOT NULL', (user_id, ))
    count = c.fetchone()[0]
    c.close()

    return count

def fetch_user_joined_date(user_id):
    c = g.database.cursor()
    c.execute('SELECT joined_date FROM users WHERE id = %s', (user_id, ))
    joined_date = c.fetchone()[0]
    c.close()

    return joined_date

def fetch_user_name(user_id):
    c = g.database.cursor()
    c.execute('SELECT username FROM users WHERE id = %s', (user_id, ))
    username = c.fetchone()[0]
    c.close()

    return username

def fetch_user_difficulty(user_id):
    c = g.database.cursor()
    c.execute('SELECT difficulty FROM users WHERE id = %s', (user_id, ))
    difficulty = c.fetchone()[0]
    c.close()

    return question.Difficulties[difficulty]
