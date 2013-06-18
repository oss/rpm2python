from app import app
from models import Cent5Packages
from models import Cent6Packages, Cent6Files, Cent6Provides, Cent6Requires
from flask import render_template, redirect, url_for
from package import PackageName
from datetime import date, timedelta
import calendar
from forms import SearchForm
from sqlalchemy import desc
import datetime
import subprocess

def buildpacknames(packages):
    packnames = []
    packname = {}
    names = []

    for package in packages:
        if package.Name not in names:
            names.append(package.Name)
            packname[package.Name] = [package]
        else:
            packname[package.Name].append(package)
    for name in names:
        packnames.append(PackageName(name, packname[name]))
    return packnames

def package2url(package):
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

@app.route('/', methods = ['GET', 'POST'])
@app.route('/index', methods = ['GET', 'POST'])
@app.route('/<string:letter>', methods = ['GET', 'POST'])
@app.route('/search/<string:searchby>/<string:search>', methods = ['GET', 'POST'])
def index(letter=None, search=None, searchby=None):
    form = SearchForm()
    if form.validate_on_submit():
        return redirect(url_for('index', search=form.function_name.data, searchby=form.searchby.data))

    if letter is None and search is None and searchby is None:
        newerthan = int(calendar.timegm((date.today() - timedelta(days=14)).timetuple()))
        packages = Cent6Packages.query.filter(Cent6Packages.Date > newerthan).order_by(desc(Cent6Packages.Date)).all()
        packages.extend(Cent5Packages.query.filter(Cent5Packages.Date > newerthan).order_by(desc(Cent6Packages.Date)).all())
        breadcrumbscontent = 'Latest'
    elif search is None and searchby is None:
        if len(letter) != 1:
            return redirect(url_for('index'))
        packages = Cent6Packages.query.filter(Cent6Packages.Name.startswith(letter)).order_by(Cent6Packages.Name).all()
        packages.extend(Cent5Packages.query.filter(Cent5Packages.Name.startswith(letter)).order_by(Cent5Packages.Name).all())
        breadcrumbscontent = letter
    else:
        if searchby == 'name':
            packages = Cent6Packages.query.filter(Cent6Packages.Name.like("%" + search + "%")).order_by(Cent6Packages.Name).all()
            packages.extend(Cent5Packages.query.filter(Cent5Packages.Name.like("%" + search + "%")).order_by(Cent5Packages.Name).all())
        elif searchby == 'file':
            packages = Cent6Packages.query.join(Cent6Files).filter(Cent6Files.Path.like("%" + search + "%")).order_by(Cent6Packages.Name).all()
            packages.extend(Cent5Packages.query.join(Cent5Files).filter(Cent5Files.Path.like("%" + search + "%")).order_by(Cent5Packages.Name).all())
        elif searchby == 'provides':
            packages = Cent6Packages.query.join(Cent6Provides).filter(Cent6Provides.Resource.like("%" + search + "%")).order_by(Cent6Packages.Name).all()
            packages.extend(Cent5Packages.query.join(Cent5Provides).filter(Cent5Provides.Resource.like("%" + search + "%")).order_by(Cent5Packages.Name).all())
        elif searchby == 'requires':
            packages = Cent6Packages.query.join(Cent6Requires).filter(Cent6Requires.Resource.like("%" + search + "%")).order_by(Cent6Packages.Name).all()
            packages.extend(Cent5Packages.query.join(Cent5Requires).filter(Cent5Requires.Resource.like("%" + search + "%")).order_by(Cent5Packages.Name).all())
        elif searchby == 'description':
            packages = Cent6Packages.query.filter(Cent6Packages.Description.like("%" + search + "%")).order_by(Cent6Packages.Name).all()
            packages.extend(Cent5Packages.query.filter(Cent5Packages.Description.like("%" + search + "%")).order_by(Cent5Packages.Name).all())
        elif searchby == 'summary':
            packages = Cent6Packages.query.filter(Cent6Packages.Summary.like("%" + search + "%")).order_by(Cent6Packages.Name).all()
            packages.extend(Cent5Packages.query.filter(Cent5Packages.Summary.like("%" + search + "%")).order_by(Cent5Packages.Name).all())

        breadcrumbscontent = 'Search'

    packnames = buildpacknames(packages)
        
    return render_template('index.html',
        packnames = packnames,
        breadcrumbscontent = breadcrumbscontent,
        form = form)

@app.route('/<int:rpm_id>/<string:dist>', methods = ['GET', 'POST'])
def package(rpm_id, dist):
    form = SearchForm()
    if form.validate_on_submit():
        return redirect(url_for('index', search=form.function_name.data, searchby=form.searchby.data))

    if 'centos6' in dist:
        package = Cent6Packages.query.filter_by(rpm_id=rpm_id).first()
        packnames = Cent6Packages.query.filter_by(Name=package.Name, Version=package.Version).order_by(Cent6Packages.Arch).all()
    else:
        package = Cent5Packages.query.filter_by(rpm_id=rpm_id).first()
        packnames = Cent5Packages.query.filter_by(Name=package.Name, Version=package.Version).order_by(Cent5Packages.Arch).all()

    breadcrumbscontent = package.Name + '-' + package.Version + '-' + package.Rel
    srcurl = package2url(package.SRCRPM)
    builton = datetime.datetime.fromtimestamp(int(package.Date)).strftime("%b %d %Y %I:%M %p")
    rpmurl = 'http://www.koji.rutgers.edu/packages/' + '/'.join([package.build_name, package.Version, package.Rel, package.Arch, '.'.join([package.nvr, package.Arch, 'rpm'])])
    print rpmurl

    subprocess.Popen('/getfile.sh ' + rpmurl, shell=True)

    return render_template('package.html',
        breadcrumbscontent = breadcrumbscontent,
        package = package,
        packnames = packnames,
        form = form,
        srcurl = srcurl,
        builton = builton)

@app.route('/test')
def test():
    package = Cent6Packages.query.filter_by(Name='pyflakes').first()

    return package.Name
