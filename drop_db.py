import psycopg2
from mathquiz import config

db = psycopg2.connect('user=%s' % config.database_user)

c = db.cursor()

c.execute('drop table if exists users')
c.execute('drop table if exists users_highscores')
c.execute('drop table if exists quiz')
c.execute('drop table if exists quiz_submissions')
c.execute('drop table if exists app_settings')

c.close()
db.commit()
