rpm2python
==========

rpm2python is used by Rutgers for viewing our CentOS packages. It is the replacement for rpm2php.
The tests use whatever database you have configured. Make sure to only run them on a test environment!

Due to a major revamp of the repotools, the populate-rpmfind-db is now included in this repository.

With this new revision, we also created a new automake installer to simplify the install experience and also
make it easier to package for Koji.

