import argparse

from mathquiz import config, database
from MxitAPI import MxitAPI

def main():
    try:
        print 'connecting to database'
        db = database.create_database()
        c = db.cursor()
        print 'connected'

        parser = argparse.ArgumentParser('MathChallenge Message Sender')
        parser.add_argument('--to', choices=['all', 'user'], help='Who are you sending this to?')
        parser.add_argument('--user', nargs=1, default=None)
        parser.add_argument('--message', help='message to be send', nargs=1)
        parser.add_argument('--file', help='file to read to send message', type=argparse.FileType('r'))

        args = parser.parse_args()

        if args.message and args.file:
            print 'Give one of file or message not both'
            return

        message = args.message
        if args.file:
            message = args.file.read()
            args.file.close()


        if args.to == 'user' and args.user:
            c.execute('SELECT username, mxit_userid FROM users WHERE mxit_userid = %s or username = %s', (args.user, args.user))
        elif args.to == 'all':
            c.execute('SELECT username, mxit_userid FROM users')
        else:
            print 'No users to select'
            return

        print 'connecting to mxit API'
        api=MxitAPI(config.client_id, config.secret_id, 'mathchallenge')
        api.auth(('message/send',))
        print 'connected'

        for username, userid in c:
            print username
            #r = api.send_message(userid, message.replace('<user>', username))
            #print 'OK' if r.ok else 'FAILURE', username

    finally:
        c.close()
        db.close()

if __name__ == '__main__':
    main()
else:
    print 'not sure what you are trying to do'
