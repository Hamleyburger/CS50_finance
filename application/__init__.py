#!/bin/env python

from flask import Flask
# flask_session could only be imported when downgrading werkzeug:
# pip uninstalled werkzeug and pip installed werkzeug==0.16.0
from flask_session import Session



# Configure application
app = Flask(__name__)

# All configs are taken from object in config.py
app.config.from_object("config.DevelopmentConfig")

# Instantiate Session
Session(app)

# Views.py must be imported AFTER instantiating the app. Otherwise circular import problems
from application import views












