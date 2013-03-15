import sys
from mathquiz import app, config
from raven.contrib.flask import Sentry

if config.sentry_enabled:
    sentry = Sentry(app, dsn=config.sentry_dsn)

if 'dev' in sys.argv:
    print 'Running in development mode'
    app.run(debug=True, host='0.0.0.0', use_debugger=True)

else:
    from tornado.wsgi import WSGIContainer
    from tornado.httpserver import HTTPServer
    from tornado.ioloop import IOLoop

    print 'Running in production mode'
    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(config.port)
    IOLoop.instance().start()
