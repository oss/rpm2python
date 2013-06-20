from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import itertools

app = Flask(__name__)
app.config.from_object('config')
db1 = SQLAlchemy(app)
db2 = SQLAlchemy(app)
app.jinja_env.globals.update(ord=ord)
app.jinja_env.globals.update(xrange=xrange)
app.jinja_env.globals.update(chr=chr)
app.jinja_env.globals.update(izip_longest=itertools.izip_longest)

from app import views, models
app.jinja_env.globals.update(unix2standard=views.unix2standard)
