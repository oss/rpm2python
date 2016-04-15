
activate_this = '/var/www/rpm2python/venv/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

from rpm2python import app as application

