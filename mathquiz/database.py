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
        session['user_id'] = c.fetchone()[0]
    except psycopg2.IntegrityError:
        # this isn't an error. We just don't check whether we've added this user before
        if 'user_id' not in session:
            raise Exception('We dont have an internal user id for the current session somehow or other')
    c.close()

    g.database.commit()

def log_quiz_answer(quiz_id, question, answer, correct):
    c = g.database.cursor()
    c.execute('INSERT INTO quiz_submissions (quiz_id, question, answer, correct) VALUES (%s, %s, %s, %s)', (quiz_id, str(question), answer, correct))
    c.close()

    g.database.commit()

def create_quiz(type):
    c = g.database.cursor()
    c.execute('INSERT INTO quiz (type, start_time, end_time, answered_by_userid) VALUES (%s, NOW(), NULL, %s)', (type, session['user_id']))
    c.execute('SELECT lastval()')
    quiz_id = c.fetchone()[0]

    c.close()

    g.database.commit()

    return quiz_id

def quiz_complete(quiz_id, num_correct, num_questions, score):
    c = g.database.cursor()
    c.execute('UPDATE quiz SET end_time = NOW(), num_correct = %s, num_questions = %s, score = %s  WHERE id = %s', (num_correct, num_questions, score, quiz_id))
    c.close()

    g.database.commit()
