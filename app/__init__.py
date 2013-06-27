from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import itertools
from config import SENDMAIL, MAIL_TO, MAIL_SUBJECT

app = Flask(__name__)
app.config.from_object('config')
db1 = SQLAlchemy(app)
db2 = SQLAlchemy(app)
app.jinja_env.globals.update(ord=ord)
app.jinja_env.globals.update(xrange=xrange)
app.jinja_env.globals.update(chr=chr)
app.jinja_env.globals.update(izip_longest=itertools.izip_longest)

if not app.debug:
    import logging
    from mail import MailHandler
    mail_handler = MailHandler(SENDMAIL, MAIL_TO, MAIL_SUBJECT)
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)

from app import views, models
app.jinja_env.globals.update(unix2standard=views.unix2standard)
