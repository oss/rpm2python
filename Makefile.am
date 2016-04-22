AUTOMAKE_OPTIONS = foreign
bindir=/usr/bin
bin_SCRIPTS = populate-rpmfind-db

RPMDIR = /var/www/rpm2python

EXTRA_DIST = run.py \
			 populate-rpmfind-db \
			 rpm2python \
			 test \
			 httpd \
			 run.py \
			 pip1.req \
			 pip2.req \
			 rpm2python.cfg.sample \
			 populate-rpmfind-db.cfg.sample \
			 run.wsgi

install-data-hook:
	mkdir $(RPMDIR); \
	groupadd rpm2python; \
	cp -r rpm2python $(RPMDIR); \
	cp -r test $(RPMDIR); \
	cp run.py $(RPMDIR); \
	cp pip1.req $(RPMDIR); \
	cp pip2.req $(RPMDIR); \
	cp rpm2python.cfg.sample /etc/rpm2python.cfg; \
	cp populate-rpmfind-db.cfg.sample /etc/populate-rpmfind-db.cfg;
	cp httpd/rpm2python.conf /etc/httpd/conf.d
	cp run.wsgi $(RPMDIR); \
	virtualenv -p `which python2` $(RPMDIR)/venv; \
	source $(RPMDIR)/venv/bin/activate; \
	pip install -r pip1.req; \
	pip install -r pip2.req; \
	cp -r /usr/lib/python2.6/site-packages/koji $(RPMDIR)/venv/lib/python2.6/site-packages; \
	cp -r /usr/lib64/python2.6/site-packages/rpm $(RPMDIR)/venv/lib/python2.6/site-packages; \
	mkdir -p /var/log/rpm2python; \
	chgrp rpm2python /var/log/rpm2python; \
	chmod 771 -R /var/log/rpm2python; \
	mkdir -p /var/lock/rpm2python; \
	chgrp rpm2python /var/lock/rpm2python; \
	chmod 771 -R /var/lock/rpm2python; \
	service httpd restart

uninstall-hook:
	rm -r $(RPMDIR); \
	rm -r /var/lock/rpm2python; \
	rm -r /var/log/rpm2python; \
	rm /etc/httpd/conf.d/rpm2python.conf; \
	service httpd restart

populate-rpmfind-db:
	chmod +x populate-rpmfind-db
