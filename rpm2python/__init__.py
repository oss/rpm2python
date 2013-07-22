from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import itertools
import tempfile

app = Flask(__name__)
app.config.from_pyfile('/etc/rpm2python.cfg')
db1 = SQLAlchemy(app)
db2 = SQLAlchemy(app)
app.jinja_env.globals.update(ord=ord)
app.jinja_env.globals.update(xrange=xrange)
app.jinja_env.globals.update(chr=chr)
app.jinja_env.globals.update(izip_longest=itertools.izip_longest)
app.jinja_env.globals.update(reversed=reversed)
app.config['TMP_DIR'] = tempfile.mkdtemp(prefix='rpm2python')

if not app.debug:
    import logging
    from mail import MailHandler
    mail_handler = MailHandler(app.config['SENDMAIL'], app.config['MAIL_TO'], app.config['MAIL_SUBJECT'])
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)

from rpm2python import views, models
app.jinja_env.globals.update(unix2standard=views.unix2standard)
