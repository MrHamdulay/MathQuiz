from mathquiz import config, database

import MxitApi

if __name__ == '__main__':
    print 'connecting to mxit API'
    api=MxitApi(config.client_id, config.secret_id, 'mathchallenge')
    api.auth(('message/send',))
    print 'connected'

    print 'connecting to database'
    db = database.create_database()
    c = db.cursor()
    print 'connected'

    i = raw_input('Message a single or all user(s)? (single / all)')
    if i[0] == 's':
        identifier = raw_input('Enter username or userid')
        c.execute('SELECT username, mxit_userid FROM users WHERE mxit_userid = %s or username = %s', (identifier, identifier))
    elif i[0] == 'a':
        c.execute('SELECT username, mxit_userid FROM users')

    message = None
    with open(raw_input('Enter path of message you wanna send:'), 'r') as f:
        message = f.read()


    for username, userid in c:
        message.replace('<user>', username)
        r = api.send_message(userid, message)
        print 'OK' if r.ok else 'FAILURE', username

    c.close()
