from mathquiz import config, database

from MxitAPI import MxitAPI

if __name__ == '__main__':

    message = None
    with open(raw_input('Enter path of message you wanna send:'), 'r') as f:
        message = f.read()
    i = raw_input('Message a single or all user(s)? (single / all)')

    print 'connecting to database'
    db = database.create_database()
    c = db.cursor()
    print 'connected'

    if i[0] == 's':
        identifier = raw_input('Enter username or userid')
        c.execute('SELECT username, mxit_userid FROM users WHERE mxit_userid = %s or username = %s', (identifier, identifier))
    elif i[0] == 'a':
        c.execute('SELECT username, mxit_userid FROM users')

    print 'connecting to mxit API'
    api=MxitAPI(config.client_id, config.secret_id, 'mathchallenge')
    api.auth(('message/send',))
    print 'connected'

    for username, userid in c:
        r = api.send_message(userid, message.replace('<user>', username))
        print 'OK' if r.ok else 'FAILURE', username

    c.close()
