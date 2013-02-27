from flask import Flask

SCHEMA_VERSION = 3
import config

app = Flask(__name__)
app.secret_key = config.secret_key

import database
import views
