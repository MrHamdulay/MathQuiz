import psycopg2
from random import randint

import mathquiz.config

db = psycopg2.connect('user=%s' % mathquiz.config.database_user)

try:
    c = db.cursor()
    for i in xrange(0, 100):
        if i % 1000 == 0:
            print i
        user_id = i*2+40
        c.execute('insert into users (username, mxit_userid) values ( %s, %s)', ('abc%d'%i, user_id))
        for d in range(2):
            if randint(0, 10) > 7:
                break
            c.execute('insert into users_highscores (userid, difficulty, highscore) values (%s, %s, %s)', (user_id, d, i*21 % 101))
    c.close()
finally:
    db.commit()
    db.close()
