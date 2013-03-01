import psycopg2

from flask import g, request, session


from mathquiz import app, config, SCHEMA_VERSION
from mathquiz.question import Question

@app.before_request
def create_database():
    g.database = psycopg2.connect('user=%s' % config.database_user)

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

def create_user():
    try:
        mxit_user_id = request.headers['HTTP_X_MXIT_USERID_R']
    except KeyError:
        print request.remote_addr
        mxit_user_id = -1 # development id
    c = g.database.cursor()
    try:
        c.execute('INSERT INTO users (mxit_userid, joined_date) VALUES (%s, NOW())', (mxit_user_id, ))
        c.execute('SELECT lastval()')
        session['userId'] = c.fetchone()[0]
        g.database.commit()
    except psycopg2.IntegrityError:
        g.database.rollback()
        # this isn't an error. We just don't check whether we've added this user before
        if 'userId' not in session:
            try:
                c2 = g.database.cursor()
                c2.execute('SELECT id, username FROM users WHERE mxit_userid = %s LIMIT 1', (str(mxit_user_id), ))
                session['userId'], session['username'] = c2.fetchone()
            finally:
                c2.close()
    finally:
        c.close()

    g.database.commit()

def set_username(username):
    c = g.database.cursor()
    c.execute('UPDATE users SET username = %s WHERE id = %s', (username, session['userId']))
    c.close()

    g.database.commit()

def log_quiz_answer(user_id, quiz_id, question, answer, correct):
    c = g.database.cursor()
    c.execute('INSERT INTO quiz_submissions (user_id, quiz_id, question, answer, correct) VALUES (%s, %s, %s, %s, %s)', (user_id, quiz_id, str(question), answer, correct))
    c.close()

    g.database.commit()

def create_quiz(type):
    c = g.database.cursor()
    c.execute('INSERT INTO quiz (type, start_time, end_time, answered_by_userid) VALUES (%s, NOW(), NULL, %s)', (type, session['userId']))
    c.execute('SELECT lastval()')
    quiz_id = c.fetchone()[0]

    c.close()

    g.database.commit()

    return quiz_id

def quiz_complete(quiz_id, num_correct, num_questions, score):
    c = g.database.cursor()
    c.execute('UPDATE quiz SET end_time = NOW(), num_correct = %s, num_questions = %s, score = %s  WHERE id = %s', (num_correct, num_questions, score, quiz_id))
    c.execute('UPDATE users SET score = score + %s WHERE id = %s', (score, session['userId']))
    c.close()

    g.database.commit()

def calculate_streak_length(user_id):
    c = g.database.cursor()
    c.execute('SELECT correct FROM quiz_submissions WHERE user_id = %s ORDER BY submit_time DESC LIMIT 10', (user_id, ))

    streakLength = 0
    for correct, in c:
        print i
        if not correct:
            break
        streakLength += 1

    c.close()

    return streakLength


def leaderboard(page):
    c = g.database.cursor()

    c.execute('SELECT username, score from users ORDER BY score DESC LIMIT 10 OFFSET %s', (page*10,))
    result = c.fetchall()
    print result
    c.close()

    return result

def username_exists(username):
    c = g.database.cursor()
    c.execute('SELECT count(*) FROM users WHERE username = %s', (username, ))
    count = c.fetchone()[0]
    c.close()

    return count > 0

def fetch_user_rank(user_id):
    c = g.database.cursor()
