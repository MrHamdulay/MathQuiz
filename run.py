import sys
import argparse

from raven.contrib.flask import Sentry
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

from mathquiz import app, config

if __name__ == '__main__':
    parser = argparse.ArgumentParser('MathChallenge')
    parser.add_argument('-p', '--port', help='Port number to listen on', nargs=1, default=config.port, type=int)
    parser.add_argument('--dev', help='Are we running the service in developer mode?', action='store_const', const=True)
    args = parser.parse_args()
    args.port = args.port[0]

    if config.sentry_enabled:
        sentry = Sentry(app, dsn=config.sentry_dsn)

    if args.dev:
        print 'Running in development mode'
        app.run(debug=True, host='0.0.0.0', port=args.port, use_debugger=True)
    else:
        print 'Running in production mode'
        http_server = HTTPServer(WSGIContainer(app))
        http_server.listen(args.port)
        IOLoop.instance().start()

