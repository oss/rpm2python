from rpm2python import app
from flask import render_template, redirect
from flask import url_for, make_response, request, abort
from flask.json import jsonify
from forms import SearchForm
from werkzeug.routing import BaseConverter
from sqlalchemy import desc, or_

from helpers import newestquery, buildpacknames, unix2standard, downunzip
from helpers import alpha_ordering, date_ordering, repos, reponames
from models import Conflicts, Files, Obsoletes, Packages, Provides, Requires
from models import Distribution

from datetime import date, timedelta
import calendar
import os
import mimetypes
import time
import shutil

class RegexConverter(BaseConverter):
    """Allows for urls to be matched to a regex"""
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]

app.url_map.converters['regex'] = RegexConverter


@app.route('/', methods = ['GET', 'POST'])
@app.route('/index', methods = ['GET', 'POST'])
@app.route('/<regex(r"[a-zA-z]"):letter>', methods = ['GET', 'POST'])
@app.route(
    '/search/<regex(r"[\w]+"):searchby>/<regex(r"[-\w/\.%_\(\)\+]*"):search>',
    methods = ['GET', 'POST'])
def index(letter=None, search=None, searchby=None):
    """View that returns the initial page (index.html)
    it extends the base layout and handles search results

    It queries the database depending on what type of URL it recieves. 
    By default, it gets packages from the last two weeks. If it gets a
    search, it will query based on the search term and selected type.
    It can also return all packages starting with the same letter.
    """
    # Check if the user arrived to this page from a search form
    # If so, they are redirected to a new page with the results
    form = SearchForm(request.form)
    if form.validate_on_submit():
        return redirect(url_for(
                            'index',
                            search=form.function_name.data,
                            searchby=form.searchby.data))
    
    packages = []
    ordering = alpha_ordering

    # If the user came to the '/' url, give them all packages
    # made in the past 2 weeks
    if letter is None and search is None and searchby is None:
        newerthan = int(calendar.timegm(
                                (date.today() - timedelta(days=14)).\
                                    timetuple()))
        packages = newestquery(
                            Packages.Date > newerthan,
                            order=desc(Packages.Date))
        breadcrumbscontent = ['Latest']
        ordering = date_ordering

    # If the user is searching by letter, find packages
    # that start with that letter
    elif search is None and searchby is None:
        if len(letter) != 1:
            return redirect(url_for('index'))
        packages = newestquery(Packages.Name.startswith(letter))
        breadcrumbscontent = [letter]

    # If the user searched, then query the correct part of
    # the database with wildcards around their keyword
    else:
        if searchby == 'name':
            packages = newestquery(
                                Packages.Name.\
                                    like("%" + search + "%"))
        elif searchby == 'file':
            packages = newestquery(
                                Files.Path.\
                                    like("%" + search + "%"),
                                join=Files)
        elif searchby == 'provides':
            packages = newestquery(
                                Provides.Resource.\
                                    like("%" + search + "%"),
                                join=Provides)
        elif searchby == 'requires':
            packages = newestquery(
                                Requires.Resource.\
                                    like("%" + search + "%"),
                                join=Requires)
        elif searchby == 'description':
            packages = newestquery(
                                Packages.Description.\
                                    like("%" + search + "%"))
        elif searchby == 'summary':
            packages = newestquery(
                                Packages.Summary.\
                                    like("%" + search + "%"))
        elif searchby == 'obsoletes':
            packages = newestquery(
                                Obsoletes.Resource.\
                                    like("%" + search + "%"),
                                join=Obsoletes)
        elif searchby == 'conflicts':
            packages = newestquery(
                                Conflicts.Resource.\
                                    like("%" + search + "%"),
                                join=Conflicts)
        else:
            abort(404)

        breadcrumbscontent = ['Search']

    packnames = buildpacknames(packages, ordering)
        
    return render_template('index.html',
        packnames = packnames,
        breadcrumbscontent = breadcrumbscontent,
        form = form)


@app.route(
    '/<regex(r"[\d]{4,5}"):rpm_id>/<regex(r"centos[56]-rutgers[-\w]*"):dist>',
    methods = ['GET', 'POST'])
@app.route('/\
    <regex(r"[\d]{4,5}"):rpm_id>/\
    <regex(r"centos[56]-rutgers[-\w]*"):dist>/getfile/\
    <regex(r"([-\w\.]+/?(?!\.))*"):f>')
def package(rpm_id, dist, f=None):
    """Returns lots of information about a particular package.
    Given an rpm_id, it returns information from the database including
    a file list, description, dependancies, and srcrpm download
    location.

    This view also allows downloading files from the package.
    """
    # check if the user got to this page through a search
    # return a results list if so
    form = SearchForm(request.form)
    if form.validate_on_submit():
        return redirect(url_for(
                            'index',
                            search=form.function_name.data,
                            searchby=form.searchby.data))

    # Find out the distribution the package is in,
    # find the package by rpm_id, and then
    # get all the other packages with the same name
    distro = []
    for repo in repos:
        if repo in dist:
            distro = [repo + '-' + x for x in reponames]
            break
    if distro == []:
        abort(404)

    package = Packages.query.\
                        filter_by(rpm_id=rpm_id).\
                        filter(
                            or_(Distribution.repo == distro[0],
                            Distribution.repo == distro[1],
                            Distribution.repo == distro[2],
                            Distribution.repo == distro[3])).first()
    if package == None:
        abort(404)
    packnames = Packages.query.\
                            filter_by(
                                Name=package.Name,
                                Version=package.Version).\
                            order_by(Packages.Arch).all()
    # Make sure to get the correct src rpm if the build_name is
    # different from the actual package name
    if package.Name != package.build_name:
        packnames.append(Packages.query.
                                    filter_by(
                                        Name=package.build_name,
                                        Version=package.Version,
                                        Arch='src').first())

    # Remove packnames from the wrong repo
    real_packnames = []
    for packname in packnames:
        for distribution in packname.distributions:
            if repo in distribution.repo:
                real_packnames.append(packname)

    # If the user is trying to download a file, download
    # the package from koji and exrtract it with rpm2cpio
    # then give the user the file
    # TODO: Get packages from /mnt/koji instead of downloading them
    if f is not None:
        rpmurl = 'http://koji.rutgers.edu/packages/' + \
                        '/'.join([
                                package.build_name,
                                package.Version,
                                package.Rel,
                                package.Arch,
                                '.'.join([
                                        package.nvr,
                                        package.Arch,
                                        'rpm'])])
        getfile = os.path.join(
                            app.config['TMP_DIR'],
                            package.build_name + str(time.time()))
        downunzip(rpmurl, getfile, f)
        f = os.path.join(getfile, f)
        try:
            resp = make_response(open(f).read())
        except IOError:
            shutil.rmtree(getfile)
            abort(500)
        mimet, encoding = mimetypes.guess_type(f)
        shutil.rmtree(getfile)
        if mimet is not None:
            resp.content_type = mimet
        else:
            resp.content_type = 'application/x-empty'
        return resp

    # Sending **kwargs instead of normal keyword arguments allows us
    # to omit some that we may not need
    kwargs = {}

    # Format the software and spec changelogs so they can be expanded
    if package.softwarechangelogs is not None:
        softchangelogsplit = package.softwarechangelogs.Text.split('\n', 5)
        if len(softchangelogsplit) <= 5:
            kwargs['softwarechangelog'] = [softchangelogsplit, '']
        else:
            kwargs['softwarechangelog'] = [
                                        softchangelogsplit[:4],
                                        softchangelogsplit[5]]
    specchangelogs = []
    packagespecchangelogs = []
    for specchangelog in package.specchangelogs:
        specchangelogs.append([x for x in specchangelog.Text.split('\n')])
        packagespecchangelogs.append(specchangelog)

    # kwargs to send to template
    kwargs['rpm_id'] = rpm_id
    kwargs['dist'] = dist
    kwargs['breadcrumbscontent'] = [package.nvr[0].upper(), package.nvr]
    kwargs['package'] = package
    kwargs['packnames'] = real_packnames
    kwargs['form'] = form
    kwargs['srcurl'] = 'http://koji.rutgers.edu/packages/' + \
                            '/'.join([
                                    package.build_name,
                                    package.Version,
                                    package.Rel,
                                    'src',
                                    package.SRCRPM])
    kwargs['builton'] = unix2standard(package.Date)
    kwargs['specchangelogs'] = specchangelogs
    kwargs['packagespecchangelogs'] = packagespecchangelogs

    return render_template('package.html', **kwargs)

@app.route('/autocomplete')
def autocomplete():
    """Does a query for all packages in the database and
    puts them into a list that is then flattened and returned as json
    """
    results = ([result.Name for result in
                                        Packages.\
                                            query.\
                                            group_by(
                                                Packages.Name).\
                                            all()])
    no_dups = []
    for name in results:
        if name not in no_dups:
            no_dups.append(name)
    ret = {}
    ret['comp'] = no_dups
    return jsonify(ret)

@app.errorhandler(404)
def page_not_found(e):
    """Just redirect to the main page if a page isn't found"""
    return redirect(url_for('index'))

@app.errorhandler(500)
def internal_server_error(e):
    """Let the user know something went wrong and that we were
    notified when a 500 occurs
    """
    return render_template('500.html',
        breadcrumbscontent=["Error"],
        form=SearchForm(request.form)), 500
