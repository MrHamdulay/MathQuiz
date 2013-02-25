import psycopg2

import config

db = psycopg2.connect('user=%s' % config.database_user)

c = db.cursor()

try:
    c.execute('create table users ('
                'id integer primary key,'
                'mxit_userid varchar(100),'
                'joined_date date)')

    c.execute('create table question_log ('
                'id integer primary key,'


    c.execute('create table quiz ('
                'id integer primary key,'
                'type varchar(20),'
                'start_time date,'
                'answered_by_userid integer,' #user id from users
                'end_time date)')

    c.execute('create table quiz_submissions ('
                'id integer primary key,'
                'quiz_id integer,'
                'question varchar(50),'
                'answer integer)') #user given answer, not necessarily correct



except psycopg2.ProgrammingError:
    print 'You have already created databases. To update schema first clear databsae. We dont upgrade '
db.commit()
