rpm2python
==========

rpm2python is used by Rutgers for viewing our CentOS packages. It is the replacement for rpm2php.

Due to a major revamp of the repotools, the populate-rpmfind-db is now included in this repository
and it is recommened to run it on a nightly cronjob instead of after every repository change, as it can be
quite time consuming.

The tests use whatever database you have configured. Make sure to only run them on a test environment!
