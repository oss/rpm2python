from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import itertools
import tempfile

import signal
import sys
import shutil

# Added for integration with populate db script
import populatedb
import _mysql
import _mysql_exceptions
from MySQLdb.constants import FIELD_TYPE
import os
import rcommon
from optparse import OptionParser

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

def run_populate_rpmfind_db(my_config_file='/etc/rutgers-repotools.cfg'):
    """ Utility to update rpmfind database """
    os.umask(002)
    myapp = rcommon.AppHandler(verifyuser=True,config_file=my_config_file)
    parser = OptionParser("usage: %prog [options]")
    parser.add_option("-r", "--rebuild",
                      default=False,
                      action="store_true",
                      help="Cleans and rebuilds the whole database.")
    parser.add_option("-v",
                      "--verbose",
                      default=False,
                      action="store_true",
                      help="Verbose output")

    (options, args) = parser.parse_args(sys.argv[1:])
    myapp.create_lock()

    if options.verbose:
        verbosity = logging.DEBUG
    else:
        verbosity = logging.INFO
    myapp.init_logger(verbosity)

    if options.rebuild: 
        my_conv = { FIELD_TYPE.LONG: int }
        db_host = myapp.config.get("rpmdb", "host")
        db_user = myapp.config.get("rpmdb", "user")
        db_pw   = myapp.config.get("rpmdb", "password")
        db_name = myapp.config.get("rpmdb", "name")

        dbase = _mysql.connect(db_host, db_user, db_pw, db_name, conv=my_conv)
        
    populatedb.clean_database(myapp, dbase)
    populatedb.create_tables(myapp, dbase)

    dbase.close()

    distname = myapp.config.get("repositories", "distname_nice")
    alldistvers = myapp.config.get("repositories", "alldistvers").split()
    for distver in alldistvers:
        myapp.distver = distver
        myapp.logger.info("Populating rpmfind database for {0} {1}...".format(
            distname, distver))
        populatedb.update_db(myapp)

    timerun = myapp.time_run()
    myapp.logger.info("\nSuccess! Time run: " + str(timerun) + " s")

    myapp.exit()
