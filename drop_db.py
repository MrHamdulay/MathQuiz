import psycopg2
from mathquiz import config

db = psycopg2.connect('user=%s' % config.database_user)

c = db.cursor()

c.execute('drop table users')
c.execute('drop table quiz')
c.execute('drop table quiz_submissions')
c.execute('drop table app_settings')

c.close()
db.commit()
