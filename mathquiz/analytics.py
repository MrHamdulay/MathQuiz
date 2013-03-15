from pyga import FlaskGATracker
from flask import request, session

from mathquiz import app, config

@app.before_request
def track():
    if config.analytics_enabled:
        tracker = FlaskGATracker(config.analytics_account, config.analytics_domain)
        tracker.track(request, session, str(session['userId']))
