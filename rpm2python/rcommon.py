""" Application handler class that contains common functions to use in our
scripts """
###############################################################################
#Programmer: Orcan Ogetbil    orcan@nbcs.rutgers.edu                          #
#Date: 10/21/2010                                                             #
#Filename: rcommon.py                                                         #
#                                                                             #
#                                                                             #
#       Copyright 2010 Orcan Ogetbil                                          #
#                                                                             #
#    This program is free software; you can redistribute it and/or modify     #
#    it under the terms of the GNU General Public License as published by     #
#    the Free Software Foundation; either version 2 of the License, or        #
#    (at your option) any later version.                                      #
#                                                                             #
#    This program is distributed in the hope that it will be useful,          #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of           #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            #
#    GNU General Public License for more details.                             #
#                                                                             #
###############################################################################

import ConfigParser
import getpass
import grp
import inspect
import koji
import logging
import os
import rlogger
import sys
import time

class AppHandler:
    """ Repotool application handler class """
    def __init__(self, verifyuser=True, config_file='../populate-rpmfind-db.cfg'):
        self.config = None
        self.load_config(config_file)
        self.username = getpass.getuser()
        self.groupowner = self.config.get("repositories", "groupowner")
        self.distname = self.config.get("repositories", "distname")
        self.distver = None
        if verifyuser:
            self.verify_user()

        # what script is calling this function?
        self._callerfile = inspect.stack()[-1][1]
        self._callername = self._callerfile.split("/")[-1]
        try:
            self._lockfilename = self.config.get("locks", "populate-rpmfind-db")
        except ConfigParser.NoOptionError:
            self._lockfilename = None

        self._start_time = time.time()
        self.logger = None
        self._logfile = None
        self._kojisession_with_ssl = None

    def init_logger(self, level=logging.INFO, quiet=False):
        """ Initialize loggers """
        self._logfile = self.config.get("logs", self._callername)
        the_suspect = self.config.get("report","user")+"-" + self.username
        rlogger.init(self._logfile, the_suspect, self.config, level, quiet)
        self.logger = logging.getLogger(the_suspect)

    def get_koji_session(self, ssl = False):
        """ Get a koji session with or without SSL access"""
        if self._kojisession_with_ssl and ssl:
            return self._kojisession_with_ssl

        hub = self.config.get('koji','hub')
        kojisession = koji.ClientSession(hub)
        if ssl:
            clientcert = self.config.get('koji','clientcert')
            clientca = self.config.get('koji','clientca')
            serverca = self.config.get('koji','serverca')
            kojisession.ssl_login(clientcert, clientca, serverca)
            self._kojisession_with_ssl = kojisession
        return kojisession

    def verify_user(self):
        """ See if we want to run our application for this user """
        if self.username == "root":
            print "Error: Please do not run this script as root."
            sys.exit(1)

        members = grp.getgrnam(self.groupowner)[3]
        if not self.username in members:
            print "Error: The user who runs this script must belong to the group: " + self.groupowner
            sys.exit(1)

    def load_config(self, config_file):
        """ Load configuration from file """
        self.config = ConfigParser.ConfigParser()
        self.config.read(config_file)

    def time_run(self):
        """ Calculate time run """
        return round(time.time() - self._start_time, 3)

    def check_lock(self):
        """ Stop if there is a lock file for this application """
        if self._lockfilename is None:
            print "No lockfile specified in the configuration for the application."
            sys.exit(1)
        lockers = self.config.options('locks')
        for locker in lockers:
            lockfilename = self.config.get('locks', locker)
            if os.path.isfile(lockfilename):
                if not AppHandler.is_running(lockfilename):
                    AppHandler.remove_lock(lockfilename)
                else:
                    print "Process is currently running. Please wait for it to finish."
                    sys.exit(1)

    def create_lock(self):
        """ Create a lock file for this application """
        self.check_lock()
        lockfile = open(self._lockfilename, "w")
        lockfile.write(str(os.getpid()))

    @staticmethod
    def remove_lock(lockfilename):
        """ Delete the lock file of this application """
        if os.path.isfile(lockfilename):
            os.remove(lockfilename)

    @staticmethod
    def is_running(lockfilename):
        lockfile = open(lockfilename, "r")
        try:
            os.kill(int(lockfile.readline()), 0)
            lockfile.close()
            return True
        except:
            lockfile.close()
            return False

    def exit(self, status=0):
        """ Exit from application gracefully """
        if self.logger:
            self.logger.debug("Beginning exit and cleanup.")
        else:
            print "Warning: Exiting, but logger has not been initialized."

        if self._lockfilename:
            AppHandler.remove_lock(self._lockfilename)

        gid = grp.getgrnam(self.groupowner)[2]

        # Check to make sure current process is in correct group
        allgroups = os.getgroups()
        if not gid in allgroups:
            self.logger.warning("Current process is not in the proper group ({0}).".format(gid))

        # Make sure the log file ends up with the right group owner:
        if self._logfile:
            if os.stat(self._logfile)[5] != gid:
                os.chown(self._logfile, -1, gid)
        sys.exit(status)
