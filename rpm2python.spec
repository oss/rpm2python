Summary:   Web-based front-end parser for Koji
Name:      rpm2python
Version:   0.8.0
Release:   1%{?dist}
License:   GPLv3
Group:     System Environment/Base
URL:       https://github.com/oss/rutgers-repotools
Source0:   %{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
BuildArch: x86_64

Requires: python, python-virtualenv
Requires: koji
Requires: httpd
Requires: mod_wsgi
BuildRequires: libtool, autoconf, automake
Requires(pre): /usr/sbin/useradd, /usr/bin/getent
Requires(postrun): /usr/sbin/userdel

%description
This package contains the necessary files to run the rpm2python koji package
information parser. 

%pre
/usr/bin/getent group rpm2python || /usr/sbin/groupadd -r rpm2python
%postun
/usr/sbin/userdel rpm2python

%prep
%setup -q
%{__aclocal}
%{__autoconf}
%{__automake} --force-missing --add-missing

%build
%configure

%install
%{__rm} -rf $RPM_BUILD_ROOT
%{__make} install DESTDIR=$RPM_BUILD_ROOT

%clean
rm -rf $RPM_BUILD_ROOT

%post
cat << EOF
If you have not done so already, you need to set up the MySQL database to be 
used by rpm2python if you have not done so already. See the Rutgers Repository 
Tools wiki page for detailed information on making the database from scratch.

The configuration files /etc/rpm2python.cfg and /etc/populate-rpmfind-db.cfg 
will need to be put on NFS and symlinked to /etc, so that other machines can 
also use the same .cfg file

More information can be found in the README file and in the OSS wiki.
EOF

%files
%defattr(-,root,root,-)
%{_bindir}/populate-rpmfind-db
%{_sysconfdir}/populate-rpmfind-db.cfg.sample
%{_sysconfdir}/rpm2python.cfg.sample
%config(noreplace) /etc/httpd/conf.d/rpm2python.conf 
%attr(4755, root, root) /var/www/rpm2python

# The log directory and lock files should be owned by the group packagepushers
%attr(4775, root, rpm2python) %dir /var/log/rpm2python/
%attr(4775, root, rpm2python) %dir /var/lock/rpm2python


%changelog
* Tue Apr 26 2016 Alexander Pavel <anp120@jla.rutgers.edu> - 0.8.0-1
- Initial packaging:
