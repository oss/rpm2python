from app import app
from models import Cent5Packages, Cent5Files, Cent5Provides, Cent5Requires
from models import Cent6Packages, Cent6Files, Cent6Provides, Cent6Requires
from flask import render_template, redirect, url_for, make_response
from package import PackageName
from datetime import date, timedelta
import calendar
from forms import SearchForm
from sqlalchemy import desc
import datetime
import subprocess
import os

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

def unix2standard(date):
    return datetime.datetime.fromtimestamp(int(date)).strftime("%b %d %Y %I:%M %p")
 
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
@app.route('/<int:rpm_id>/<string:dist>/getfile/<path:f>')
def package(rpm_id, dist, f=None):
    form = SearchForm()
    if form.validate_on_submit():
        return redirect(url_for('index', search=form.function_name.data, searchby=form.searchby.data))

    if 'centos6' in dist:
        package = Cent6Packages.query.filter_by(rpm_id=rpm_id).first()
        packnames = Cent6Packages.query.filter_by(Name=package.Name, Version=package.Version).order_by(Cent6Packages.Arch).all()
    else:
        package = Cent5Packages.query.filter_by(rpm_id=rpm_id).first()
        packnames = Cent5Packages.query.filter_by(Name=package.Name, Version=package.Version).order_by(Cent5Packages.Arch).all()

    if f is not None:
        rpmurl = 'http://koji.rutgers.edu/packages/' + '/'.join([package.build_name, package.Version, package.Rel, package.Arch, '.'.join([package.nvr, package.Arch, 'rpm'])])
        subprocess.Popen('./getfile.sh ' + rpmurl, stdout=open(os.devnull, 'wb'), shell=True)
        resp = make_response(open('getfile/' + f).read())
        return resp

    breadcrumbscontent = package.Name + '-' + package.Version + '-' + package.Rel
    srcurl = package2url(package.SRCRPM)
    builton = unix2standard(package.Date)
    softwarechangelog = ""
    if package.softwarechangelogs is not None:
        softchangelogsplit = package.softwarechangelogs.Text.split('\n', 5)
        softwarechangelog = [softchangelogsplit[:4], softchangelogsplit[5]]
    specchangelogs = []
    for specchangelog in package.specchangelogs:
        specchangelogs.append(specchangelog.Text.split('\n'))

    return render_template('package.html',
        rpm_id = rpm_id,
        dist = dist,
        breadcrumbscontent = breadcrumbscontent,
        package = package,
        packnames = packnames,
        form = form,
        srcurl = srcurl,
        builton = builton,
        softwarechangelog = softwarechangelog,
        specchangelogs = specchangelogs)
