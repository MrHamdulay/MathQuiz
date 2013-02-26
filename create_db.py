import psycopg2

from mathquiz import config, SCHEMA_VERSION

db = psycopg2.connect('user=%s' % config.database_user)

c = db.cursor()

try:
    c.execute('create table users ('
                'id SERIAL,'
                'mxit_userid varchar(100) unique,'
                'joined_date date)')

    c.execute('create table quiz ('
                'id SERIAL,'
                'type varchar(20),'
                'start_time date,'
                'answered_by_userid integer,' #user id from users
                'num_correct integer,'
                'num_questions integer,'
                'score integer,'
                'end_time date)')

    c.execute('create table quiz_submissions ('
                'id SERIAL,'
                'quiz_id integer,'
                'question varchar(50),'
                'answer integer,'
                'correct boolean)') #user given answer, not necessarily correct

    c.execute('create table app_settings ('
                'key varchar, '
                'value varchar)')
    c.execute("insert into app_settings (key, value) values ('schema_version', '%s')", (SCHEMA_VERSION, ))
    db.commit()
except psycopg2.ProgrammingError, e:
    print 'You have already created databases. To update schema first clear databsae. We dont upgrade '
    print e
finally:
    c.close()
    db.close()
