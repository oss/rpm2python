AUTOMAKE_OPTIONS = foreign
bindir=/usr/bin
bin_SCRIPTS = populate-rpmfind-db

INST_DIR = /var/www/rpm2python

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
			 run.wsgi \
			 venv.tar.gz

install-data-hook:
	mkdir -p $(DESTDIR)$(INST_DIR); \
	cp -r rpm2python $(DESTDIR)$(INST_DIR); \
	cp -r venv $(DESTDIR)$(INST_DIR); \
	cp -r test $(DESTDIR)$(INST_DIR); \
	cp run.py $(DESTDIR)$(INST_DIR); \
	cp pip1.req $(DESTDIR)$(INST_DIR); \
	cp pip2.req $(DESTDIR)$(INST_DIR); \
	mkdir -p $(DESTDIR)/etc; \
	cp rpm2python.cfg.sample $(DESTDIR)/etc/rpm2python.cfg.sample; \
	cp populate-rpmfind-db.cfg.sample $(DESTDIR)/etc/populate-rpmfind-db.cfg.sample; \
	mkdir -p $(DESTDIR)/etc/httpd/conf.d; \
	cp httpd/rpm2python.conf $(DESTDIR)/etc/httpd/conf.d/rpm2python.conf; \
	cp run.wsgi $(DESTDIR)$(INST_DIR); \
	mkdir -p $(DESTDIR)/var/log/rpm2python; \
	mkdir -p $(DESTDIR)/var/lock/rpm2python; 

uninstall-hook:
	rm -r $(DESTDIR)/$(INST_DIR); \
	rm -r $(DESTDIR)/var/lock/rpm2python; \
	rm -r $(DESTDIR)/var/log/rpm2python; \
	rm $(DESTDIR)/etc/httpd/conf.d/rpm2python.conf;

populate-rpmfind-db:
	chmod +x populate-rpmfind-db
