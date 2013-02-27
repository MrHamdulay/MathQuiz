import psycopg2

from mathquiz import config, SCHEMA_VERSION

db = psycopg2.connect('user=%s' % config.database_user)

c = db.cursor()

try:
    c.execute('CREATE TABLE users ('
                'id SERIAL,'
                'username VARCHAR UNIQUE,'
                'mxit_userid varchar(100) UNIQUE,'
                'joined_date timestamp DEFAULT NOW(),'
                'score integer DEFAULT 0'
                ')')
    c.execute('CREATE INDEX ON users (score)')

    c.execute('CREATE TABLE quiz ('
                'id SERIAL,'
                'type varchar(20),'
                'start_time timestamp,'
                'answered_by_userid integer,' #user id from users
                'num_correct integer,'
                'num_questions integer,'
                'score integer,'
                'end_time timestamp)')
    c.execute('CREATE INDEX complete_time ON quiz ((end_time - start_time))')


    c.execute('CREATE TABLE quiz_submissions ('
                'id SERIAL,'
                'quiz_id INTEGER,'
                'question VARCHAR(50),'
                'answer INTEGER,'
                'correct BOOLEAN)') #user given answer, not necessarily correct

    c.execute('CREATE TABLE app_settings ('
                'key VARCHAR, '
                'value VARCHAR)')
    c.execute("INSERT INTO app_settings (key, value) VALUES ('schema_version', '%s')", (SCHEMA_VERSION, ))
    db.commit()
except psycopg2.ProgrammingError, e:
    print 'You have already created databases. To update schema first clear databsae. We dont upgrade '
    print e
finally:
    c.close()
    db.close()
