from app import db1, db2
from models import Cent6Packages, Cent6Files, Cent6Provides, Cent6Requires, Cent6Obsoletes, Cent6Conflicts, Cent6Distribution, Cent6ChangeLogs, Cent6SoftwareChangeLogs, Cent6SpecChangeLogs
from models import Cent5Packages, Cent5Files, Cent5Provides, Cent5Requires, Cent5Obsoletes, Cent5Conflicts, Cent5Distribution, Cent5ChangeLogs, Cent5SoftwareChangeLogs, Cent5SpecChangeLogs
from package import PackageName
from sqlalchemy import func
import datetime

distros = ['cent6', 'cent5']

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

#puts the given list of packages into a container object called PackageName
#this stores all packages of the same name together
def buildpacknames(packages):
    packnames = []
    packname = {}
    names = []

    for cent in packages:
        for package in cent:
            if package[0].Name not in names:
                names.append(package[0].Name)
                packname[package[0].Name] = [package]
            else:
                packname[package[0].Name].append(package)
    
    for name in names:
        packnames.append(PackageName(name, packname[name]))
    return packnames

#this converts a package name to a url in koji
#it will probably be removed in refactoring
def SRCRPM2url(package):
    ret = 'http://koji.rutgers.edu/packages/'
    words = package.split('-')
    last = words[-1].split('.')
    words[-1] = last[0] + '.' + last[1]
    words.append(last[2])
    for word in words:
        if word != 'debuginfo':
            ret += word + '/'
    ret += package
    return ret

#converts a unix timestamp to a human readable format
def unix2standard(date):
    return datetime.datetime.fromtimestamp(int(date)).strftime("%b %d %Y %I:%M %p")

def newestquery(distro, queryfilter, order=None, join=None):
    if order is None:
        order = Packages[distro].Name
    if join is None:
        return dbs[distro].session.query(Packages[distro], Distribution[distro].repo, func.max(Packages[distro].Date)).join(Distribution[distro]).filter(queryfilter, Packages[distro].Arch != 'src').group_by(Packages[distro].Name, Distribution[distro].repo).order_by(order).all()
    else:
        return dbs[distro].session.query(Packages[distro], Distribution[distro].repo, func.max(Packages[distro].Date)).join(Distribution[distro]).outerjoin(join).filter(queryfilter, Packages[distro].Arch != 'src').group_by(Packages[distro].Name, Distribution[distro].repo).order_by(order).all()
