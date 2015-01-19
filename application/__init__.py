import json, os, re, sys
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

# Create the Skeleton app
app = Flask(__name__, static_path='/static')
db = SQLAlchemy(app)
app.config.from_object('config')
from application import views, models
