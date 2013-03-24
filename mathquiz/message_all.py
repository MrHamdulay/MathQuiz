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

    message = raw_input('Enter message you wish to send to users: ')

    users = [userid for username, userid in c]

    r = api.send_message(users, message)
    print r
    print r.text

    c.close()
