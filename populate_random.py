import psycopg2
from random import randint

import mathquiz.config

db = psycopg2.connect('user=%s' % mathquiz.config.database_user)

try:
    c = db.cursor()
    for i in xrange(0, 100):
        if i % 1000 == 0:
            print i
        c.execute('insert into users (username, mxit_userid, score) values (%s, %s, %s)', ('abc%d'%i, i*2+40, (i) % 1001))
    c.close()
finally:
    db.commit()
    db.close()
