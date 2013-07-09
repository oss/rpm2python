from rpm2python import app
from flask import render_template, redirect, url_for, make_response, request, abort
from flask.json import jsonify
from forms import SearchForm
from werkzeug.routing import BaseConverter
from sqlalchemy import desc

from helpers import newestquery, buildpacknames, SRCRPM2url, unix2standard, downunzip
from helpers import Conflicts, Files, Obsoletes, Packages, Provides, Requires
from helpers import distros, dbs

from datetime import date, timedelta
import calendar
import os
import mimetypes
import itertools

#allows for urls to be matched to a regex
class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]

app.url_map.converters['regex'] = RegexConverter

#view that returns the initial page (index.html)
#it extends the base layout and handles search results
@app.route('/', methods = ['GET', 'POST'])
@app.route('/index', methods = ['GET', 'POST'])
@app.route('/<regex("[a-zA-z]"):letter>', methods = ['GET', 'POST'])
@app.route('/search/<regex("[\w]+"):searchby>/<regex("[-\w/\.%]*"):search>', methods = ['GET', 'POST'])
def index(letter=None, search=None, searchby=None):
    #checks if the user arrived to this page from a search form
    #if so, they are redirected to a new page with the results
    form = SearchForm(request.form)
    if form.validate_on_submit():
        return redirect(url_for('index', search=form.function_name.data, searchby=form.searchby.data))
    
    packages = []

    #if the user came to the '/' url, give them all packages made in the past 2 weeks
    if letter is None and search is None and searchby is None:
        newerthan = int(calendar.timegm((date.today() - timedelta(days=14)).timetuple()))
        for distro in distros:
            packages.append(newestquery(distro, Packages[distro].Date > newerthan, order=desc(Packages[distro].Date)))
        breadcrumbscontent = 'Latest'
    #if the user is searching by letter, find packages that start with that letter
    elif search is None and searchby is None:
        if len(letter) != 1:
            return redirect(url_for('index'))
        for distro in distros:
            packages.append(newestquery(distro, Packages[distro].Name.startswith(letter)))
        breadcrumbscontent = letter
    #if the user searched, then query the correct part of the database with wildcards around their keyword
    else:
        for distro in distros:
            if searchby == 'name':
                packages.append(newestquery(distro, Packages[distro].Name.like("%" + search + "%")))
            elif searchby == 'file':
                packages.append(newestquery(distro, Files[distro].Path.like("%" + search + "%"), join=Files[distro]))
            elif searchby == 'provides':
                packages.append(newestquery(distro, Provides[distro].Resource.like("%" + search + "%"), join=Provides[distro]))
            elif searchby == 'requires':
                packages.append(newestquery(distro, Requires[distro].Resource.like("%" + search + "%"), join=Requires[distro]))
            elif searchby == 'description':
                packages.append(newestquery(distro, Packages[distro].Description.like("%" + search + "%")))
            elif searchby == 'summary':
                packages.append(newestquery(distro, Packages[distro].Summary.like("%" + search + "%")))
            elif searchby == 'obsoletes':
                packages.append(newestquery(distro, Obsoletes[distro].Resource.like("%" + search + "%"), join=Obsoletes[distro]))
            elif searchby == 'conflicts':
                packages.append(newestquery(distro, Conflicts[distro].Resource.like("%" + search + "%"), join=Conflicts[distro]))
            else:
                abort(404)


        breadcrumbscontent = 'Search'

    packnames = buildpacknames(packages)
        
    return render_template('index.html',
        packnames = packnames,
        breadcrumbscontent = breadcrumbscontent,
        form = form)

#returns a page with info about the package that the user queried
@app.route('/<regex("[\d]{4,5}"):rpm_id>/<regex("centos[56]-rutgers[-\w]*"):dist>', methods = ['GET', 'POST'])
@app.route('/<regex("[\d]{4,5}"):rpm_id>/<regex("centos[56]-rutgers[-\w]*"):dist>/getfile/<regex("([-\w\.]+/?(?!\.))*"):f>')
def package(rpm_id, dist, f=None):
    #check if the user got to this page through a search
    #return a results list if so
    form = SearchForm(request.form)
    if form.validate_on_submit():
        return redirect(url_for('index', search=form.function_name.data, searchby=form.searchby.data))

    #find out the distribution the package is in
    #find the package by rpm_id and then get all the other packages with the same name
    if 'centos6' in dist:
        package = Packages['cent6'].query.filter_by(rpm_id=rpm_id).first()
        packnames = Packages['cent6'].query.filter_by(Name=package.Name, Version=package.Version).order_by(Packages['cent6'].Arch).all()
    elif 'centos5' in dist:
        package = Packages['cent5'].query.filter_by(rpm_id=rpm_id).first()
        packnames = Packages['cent5'].query.filter_by(Name=package.Name, Version=package.Version).order_by(Packages['cent5'].Arch).all()
    else:
        abort(404)

    #if the user is trying to download a file, download the package from koji and exrtract it with rpm2cpio
    #then give the user the file
    if f is not None:
        rpmurl = 'http://koji.rutgers.edu/packages/' + '/'.join([package.build_name, package.Version, package.Rel, package.Arch, '.'.join([package.nvr, package.Arch, 'rpm'])])
        getfile = os.path.join(os.path.dirname(__file__), 'getfile')
        downunzip(rpmurl, getfile)
        f = os.path.join(getfile, f)
        resp = make_response(open(f).read())
        mimet, encoding = mimetypes.guess_type(f)
        if mimet is not None:
            resp.content_type = mimet
        else:
            resp.content_type = 'application/x-empty'
        return resp

    #a few extra variables that will be needed to print out in the template
    breadcrumbscontent = package.Name + '-' + package.Version + '-' + package.Rel
    srcurl = SRCRPM2url(package.SRCRPM)
    builton = unix2standard(package.Date)
    softwarechangelog = ""
    if package.softwarechangelogs is not None:
        softchangelogsplit = package.softwarechangelogs.Text.split('\n', 5)
        softwarechangelog = [softchangelogsplit[:4], softchangelogsplit[5]]
    specchangelogs = []
    packagespecchangelogs = []
    for specchangelog in package.specchangelogs:
        specchangelogs.append(specchangelog.Text.split('\n'))
        packagespecchangelogs.append(specchangelog)

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
        specchangelogs = specchangelogs,
        packagespecchangelogs = packagespecchangelogs)

#does a query for all packages in the database and puts them into a list that is then flattened and returned as a string
#don't laugh, I don't acutally know any javascript
@app.route('/autocomplete')
def autocomplete():
    results = []
    for distro in distros:
        results.append(dbs[distro].session.query(Packages[distro].Name).group_by(Packages[distro].Name).all())
    flattened = list(itertools.chain.from_iterable(results[0]))
    ret = {}
    ret['comp'] = flattened
    return jsonify(ret)

@app.errorhandler(404)
def page_not_found(e):
    return redirect(url_for('index'))

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html',
        breadcrumbscontent="Error",
        form=SearchForm(request.form)), 500
