from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import itertools
import tempfile

import signal
import sys
import shutil

app = Flask(__name__)
app.config.from_pyfile('../rpm2python.cfg')

db = SQLAlchemy(app)

app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True
app.jinja_env.globals.update(ord=ord)
app.jinja_env.globals.update(xrange=xrange)
app.jinja_env.globals.update(chr=chr)
app.jinja_env.globals.update(izip=itertools.izip)
app.jinja_env.globals.update(reversed=reversed)
app.jinja_env.globals.update(len=len)

app.config['TMP_DIR'] = tempfile.mkdtemp(prefix='rpm2python')

def signal_handler(signal, frame):
    """Make sure to delete the temp folders when we're stopped"""
    global app
    shutil.rmtree(app.config['TMP_DIR'])
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

if not app.debug:
    # Send mail when something goes wrong
    import logging
    from mail import MailHandler
    mail_handler = MailHandler(
                        app.config['SENDMAIL'],
                        app.config['MAIL_TO'],
                        app.config['MAIL_SUBJECT'])
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)

from rpm2python import views, models
app.jinja_env.globals.update(unix2standard=views.unix2standard)
