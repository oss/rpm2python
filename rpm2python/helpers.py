from rpm2python import db1, db2, app

from models import Cent6Packages, Cent6Files, Cent6Provides, Cent6Requires
from models import Cent6Obsoletes, Cent6Conflicts, Cent6Distribution
from models import Cent6ChangeLogs, Cent6SoftwareChangeLogs
from models import Cent6SpecChangeLogs

from models import Cent5Packages, Cent5Files, Cent5Provides, Cent5Requires
from models import Cent5Obsoletes, Cent5Conflicts, Cent5Distribution
from models import Cent5ChangeLogs, Cent5SoftwareChangeLogs
from models import Cent5SpecChangeLogs

from sqlalchemy import func, not_, and_
from sqlalchemy.orm import aliased
import datetime
import os
import subprocess

'''This set of dictionaries allows easy access to the database.
Because the databases are identical, you can change which database
you are querying by changing the key.
Add more if more databases are added
'''
distros = ['cent6', 'cent5']
repos = ['centos6', 'centos5']

dbs = {
    'cent6': db1,
    'cent5': db2}

ChangeLogs = {
    'cent6': Cent6ChangeLogs,
    'cent5': Cent5ChangeLogs}

Conflicts = {
    'cent6': Cent6Conflicts,
    'cent5': Cent5Conflicts}

Distribution = {
    'cent6': Cent6Distribution,
    'cent5': Cent5Distribution}

Files = {
    'cent6': Cent6Files,
    'cent5': Cent5Files}

Obsoletes = {
    'cent6': Cent6Obsoletes,
    'cent5': Cent5Obsoletes}

Packages = {
    'cent6': Cent6Packages,
    'cent5': Cent5Packages}

Provides = {
    'cent6': Cent6Provides,
    'cent5': Cent5Provides}

Requires = {
    'cent6': Cent6Requires,
    'cent5': Cent5Requires}

SoftwareChangeLogs = {
    'cent6': Cent6SoftwareChangeLogs,
    'cent5': Cent5SoftwareChangeLogs}

SpecChangeLogs = {
    'cent6': Cent6SpecChangeLogs,
    'cent5': Cent5SpecChangeLogs}

class PackageName():
    """PackageName is used in the index template for ordering purposes
    it groups packages of the same name together, and gets
    the latest version from each repo to display it

    name: name shared by the packages
    archs: the architectures of the packages
    packages: the actual packages, these are
        the newest in each repo with this name
    """
    def __init__(self, name, archs, packages):
        self.name = name
        self.packages = packages
        self.archs = archs
        self.repos = {
                'stable': ['{0}-rutgers'.format(x) for x in repos],
                'testing': ['{0}-rutgers-testing'.format(x) for x in repos],
                'unstable': ['{0}-rutgers-unstable'.format(x) for x in repos],
                }
        fakepack = Cent6Packages()
        fakepack.Version = ""
        fakepack.Rel = ""
        self.newest = {}
        for genrepo in self.repos:
            for repo in self.repos[genrepo]:
                self.newest[repo] = fakepack
        for package in self.packages:
            self.newest[package[1]] = package[0]


def alpha_ordering(package1, package2):
    return True if package1.Name < package2.Name else False


def date_ordering(package1, package2):
    return False if package1.Date < package2.Date else True


def buildpacknames(packages, ordering):
    """Puts the given list of packages into a
    container object called PackageName this stores all packages
    of the same name together. It also sorts the list while doing
    this.

    packages is a list of lists of tuples
    The first tier is the distributions. Each list in the first list
    will be from a certain ditribution. In each of those lists is
    a tuple of the form (CentXPackage, repo, date). Only the first
    one is really needed, but the rest is returned by a SQL query.

    This function is not supposed to make sense.
    
    IF ALL ENTRIES WERE IN ONE DATABASE THIS WOULDN'T BE NECCESSARY
    CONSIDER MAKING THE DATABASE BETTER BEFORE MESSING WITH THIS
    """
    packnames = []
    packname = {}
    names = []
    archname = {}
    
    indexes = []
    for distro in packages:
        indexes.append(0)

    merged = False
    ordered = []
    while not merged:
        package = (Cent6Packages(), None, None)
        package[0].Name = '{'
        num_merged = 0
        package_distro = 0
        for distro in xrange(0, len(packages)):
            index = indexes[distro]
            if index == len(packages[distro]):
                num_merged += 1
            elif ordering(packages[distro][index][0], package[0]):
                package = packages[distro][index]
                package_distro = distro
            if num_merged == len(packages):
                merged = True
        if merged == False:
            indexes[package_distro] += 1
            ordered.append(package)
            if package[0].Name not in names:
                names.append(package[0].Name)
                archname[package[0].Name] = [package[0].Arch]
                packname[package[0].Name] = [package]
            elif package[0].Arch not in archname[package[0].Name]:
                archname[package[0].Name].append(package[0].Arch)
            else:
                packname[package[0].Name].append(package)

    for name in names:
        packnames.append(PackageName(name, archname[name], packname[name]))
    return packnames


def downunzip(rpmurl, getfile, f):
    """Downloads and unzips the rpm at rpmurl to the directory
    getfile/f.
    """
    if os.path.exists(os.path.join(getfile, f)):
        return
    cwd = os.getcwd()
    os.makedirs(getfile)
    os.chdir(getfile)
    subprocess.Popen(['/usr/bin/wget', rpmurl]).wait()
    rpm2cpio = subprocess.Popen(
                        ['/usr/bin/rpm2cpio', os.listdir(getfile)[0]],
                        stdout=subprocess.PIPE)
    subprocess.Popen(['/bin/cpio', '-idmv'],
                stdin=rpm2cpio.stdout, stdout=subprocess.PIPE).wait()
    rpm2cpio.stdout.close()
    os.chdir(cwd)


def unmask(mask):
    """Flags on dependancies in the database are stored as a bitmask.
    This method returns the symbol specified by the flag.
    """
    output = ""
    if 2 & mask:
        output += "<"
    if 4 & mask:
        output += ">"
    if 8 & mask:
        output += "="
    return output


def readsize(byte_s):
    """Convert bytes to a readable format"""
    if byte_s / 1024 == 0:
        return "{0} B".format(byte_s)
    byte_s /= 1024
    if byte_s / 1024 == 0:
        return "{0} KB".format(byte_s)
    return "{0} MB".format(byte_s / 1024)


# Allow jinja to use these methods
app.jinja_env.globals.update(unmask=unmask)
app.jinja_env.globals.update(readsize=readsize)


def unix2standard(date):
    """converts a unix timestamp to a human readable format"""
    return datetime.datetime.fromtimestamp(
                                    int(date)).strftime("%b %d %Y %I:%M %p")

def newestquery(distro, queryfilter, order=None, join=None):
    """A shortcut for a common SQL query I use. It gets the newest
    packages of a certain name. Check views.py/index to get an idea
    of how it's used.
    """
    if order is None:
        order = Packages[distro].Name
    p1 = aliased(Packages[distro])
    d1 = aliased(Distribution[distro])
    if join is None:
        sq = dbs[distro].session.\
                            query(
                                Packages[distro].Name,
                                Packages[distro].Arch,
                                Distribution[distro].repo,
                                func.max(Packages[distro].Date).\
                                                            label('Date')).\
                            select_from(
                                Packages[distro]).\
                            join(
                                Distribution[distro]).\
                            filter(
                                queryfilter).\
                            filter(
                                not_(Distribution[distro].repo.\
                                                        like('%staging'))).\
                            group_by(
                                Packages[distro].Name,
                                Packages[distro].Arch,
                                Distribution[distro].repo).subquery()
    else:
        sq = dbs[distro].session.\
                            query(
                                Packages[distro].Name,
                                Packages[distro].Arch,
                                Distribution[distro].repo,
                                func.max(Packages[distro].Date).\
                                                            label('Date')).\
                            select_from(
                                Packages[distro]).\
                            join(
                                Distribution[distro]).\
                            join(
                                join).\
                            filter(
                                queryfilter).\
                            filter(
                                not_(Distribution[distro].repo.\
                                                        like('%staging'))).\
                            group_by(
                                Packages[distro].Name,
                                Packages[distro].Arch,
                                Distribution[distro].repo).subquery()
    return dbs[distro].session.\
                            query(
                                p1, d1.repo).\
                            join(
                                d1).\
                            join(
                                sq,
                                and_(sq.c.Name==p1.Name,
                                sq.c.Arch==p1.Arch,
                                sq.c.repo==d1.repo,
                                sq.c.Date==p1.Date)).\
                            order_by(p1.nvr, p1.Arch).all()
