AUTOMAKE_OPTIONS = foreign
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
			 populate-rpmfind-db.cfg.sample

install-data-hook:
	mkdir $(RPMDIR); \
	cp -r rpm2python $(RPMDIR); \
	cp -r test $(RPMDIR); \
	cp run.py $(RPMDIR); \
	cp pip1.req $(RPMDIR); \
	cp pip2.req $(RPMDIR); \
	cp rpm2python.cfg.sample /etc/rpm2python.cfg; \
	cp populate-rpmfind-db.cfg.sample /etc/populate-rpmfind-db.cfg;
	cp httpd/rpm2python.conf /etc/httpd/conf.d
	virtualenv -p `which python2` $(RPMDIR)/venv; \
	source $(RPMDIR)/venv/bin/activate; \
	pip install -r pip1.req; \
	pip install -r pip2.req;

uninstall-hook:
	rm -r $(RPMDIR)

populate-rpmfind-db:
	chmod +x populate-rpmfind-db
