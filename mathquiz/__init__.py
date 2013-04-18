from flask import Flask, g

APP_NAME = 'mathchallenge'
SCHEMA_VERSION = 10
import config

app = Flask(__name__)
app.secret_key = config.secret_key

import database
import views

import analytics

import ads

@app.context_processor
def inject_ad():
    def ad():
        return ads.generate_ad(config.shinka_advert_id)

    return dict(ad=ad)
