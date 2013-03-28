from flask import Flask, g

SCHEMA_VERSION = 10
import config

app = Flask(__name__)
app.secret_key = config.secret_key

import database
import views

import analytics