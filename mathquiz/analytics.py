from pyga import FlaskGATracker
from flask import request, session

import subprocess
import base64
import simplejson
from time import time

from mathquiz import app, config

@app.before_request
def google_track():
    if config.analytics_enabled:
        tracker = FlaskGATracker(config.analytics_account, config.analytics_domain)
        tracker.track(request, session, str(session['userId']))

if config.mixpanel_enabled:
    def track(event, properties=None):
        """
        A simple function for asynchronously logging to the mixpanel.com API.
        This function requires `curl` and Python version 2.4 or higher.

        @param event: The overall event/category you would like to log this data under
        @param properties: A dictionary of key-value pairs that describe the event
                           See http://mixpanel.com/api/ for further detail.
        @return Instance of L{subprocess.Popen}
        """
        if properties == None:
            properties = {}

        token = config.mixpanel_token
        properties['distinct_id'] = session['userId']
        properties['mp_name_tag'] = session['username']
        properties['time'] = str(int(time))

        if "token" not in properties:
            properties["token"] = token

        database.add_analytics(event, properties)

        params = {"event": event, "properties": properties}
        data = base64.b64encode(simplejson.dumps(params))
        request = "http://api.mixpanel.com/track/?data=" + data
        return subprocess.Popen(("curl",request), stderr=subprocess.PIPE,
            stdout=subprocess.PIPE)
else:
    def track(*args):
        print 'not tracking. mixpanel disabled', args
        pass
