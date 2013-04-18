from pyga import FlaskGATracker
from flask import request, session, g
import statsd

import subprocess
import base64
import simplejson
from time import time

from mathquiz import app, config

def add_analytics_db(event, properties):
    c = g.database.cursor()
    params = simplejson.dumps({'event':event, 'properties':properties})
    c.execute('INSERT INTO analytics_queue (data) values (%s)', (params, ))
    c.execute('NOTIFY analytics')
    c.close()
    g.database.commit()

@app.before_request
def google_track():
    if config.analytics_enabled:
        tracker = FlaskGATracker(config.analytics_account, config.analytics_domain)
        tracker.track(request, session, str(session['userId']))

if config.mixpanel_enabled:
    def track(event, properties=None):
        if session['username'] == 'Yasen':
            return
        if properties == None:
            properties = {}

        token = config.mixpanel_token
        properties['distinct_id'] = session['userId']
        properties['username'] = properties['mp_name_tag'] = session['username']
        properties['time'] = int(time())
        if 'X-Forwarded-For' in request.headers:
            properties['ip'] = request.headers['X-Forwarded-For']

        if "token" not in properties:
            properties["token"] = token

        add_analytics_db(event, properties)

else:
    def track(*args):
        print 'not tracking. mixpanel disabled', args
        pass

stats = statsd.StatsClient(config.statsd_server, config.statsd_port)
