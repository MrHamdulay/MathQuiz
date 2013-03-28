import psycopg2

from mathquiz import config, SCHEMA_VERSION

db = psycopg2.connect('user=%s' % config.database_user)

c = db.cursor()

try:
    c.execute('CREATE TABLE users ('
                'id SERIAL,'
                'username VARCHAR UNIQUE,'
                'difficulty INTEGER DEFAULT 0,'
                'mxit_userid varchar(100) UNIQUE,'
                'joined_date timestamp DEFAULT NOW()'
                ')')
    c.execute('CREATE TABLE users_highscores ('
                'id SERIAL,'
                'userid INTEGER,'
                'difficulty INTEGER,' # add ten for streak stuff
                'highscore INTEGER NOT NULL DEFAULT 0'
                ')')
    c.execute('CREATE UNIQUE INDEX highscores ON users_highscores (userid, difficulty)')

    c.execute('CREATE TABLE quiz ('
                'id SERIAL,'
                'type varchar(20),'
                'start_time timestamp,'
                'user_id integer,' #user id from users
                'num_correct integer,'
                'num_questions integer,'
                'score integer,'
                'end_time timestamp)')
    c.execute('CREATE INDEX complete_time ON quiz ((end_time - start_time))')

    c.execute('CREATE TABLE quiz_submissions ('
                'id SERIAL,'
                'user_id INTEGER,'
                'quiz_id INTEGER,'
                'question VARCHAR(50),'
                'answer INTEGER,'
                'correct BOOLEAN,'
                'score INTEGER,'
                'submit_time TIMESTAMP DEFAULT NOW()'
                ')') #user given answer, not necessarily correct
    c.execute('CREATE INDEX streak ON quiz_submissions (user_id, submit_time, correct)')
    c.execute('CREATE index quiz_submissions_by_id ON quiz_submissions (quiz_id)')

    c.execute('CREATE TABLE app_settings ('
                'key VARCHAR, '
                'value VARCHAR)')
    c.execute("INSERT INTO app_settings (key, value) VALUES ('schema_version', '%s')", (SCHEMA_VERSION, ))

    c.execute('CREATE TABLE feedback (username VARCHAR,'
                    'userid INTEGER,'
                    'feedback TEXT, '
                    'submitted_date TIMESTAMP DEFAULT NOW()'
                    ')')

    c.execute('CREATE TABLE analytics_queue (id SERIAL, data TEXT)')


    db.commit()
except psycopg2.ProgrammingError, e:
    print 'You have already created databases. To update schema first clear databsae. We dont upgrade '
    print e
finally:
    c.close()
    db.close()
