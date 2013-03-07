import sys
from mathquiz import app, config

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
