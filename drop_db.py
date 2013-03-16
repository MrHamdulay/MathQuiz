import psycopg2
from mathquiz import config
import sys

print 'Are you sure this is what you want to do? Say YES to confirm'
if raw_input() != 'YES':
    sys.exit()
db = psycopg2.connect('user=%s' % config.database_user)

c = db.cursor()

c.execute('drop table if exists users')
c.execute('drop table if exists users_highscores')
c.execute('drop table if exists quiz')
c.execute('drop table if exists quiz_submissions')
c.execute('drop table if exists app_settings')
c.execute('drop table if exists feedback')
c.execute('drop table if exists analytics_queue')

c.close()
db.commit()
print 'Completed'
