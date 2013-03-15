from pyga import FlaskGATracker
from flask import request, session

from mathquiz import app, config

@app.before_request
def track():
    tracker = FlaskGATracker(config.analytics_account, config.analytics_domain)
    tracker.track(request, session)
