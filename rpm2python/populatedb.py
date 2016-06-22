""" Library that populates our rpm database """

###############################################################################
#Programmer: Orcan Ogetbil    orcan@nbcs.rutgers.edu                          #
#Date: 10/27/2010                                                             #
#Filename: populatedb.py                                                      #
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

import os
import string
import _mysql
import _mysql_exceptions
from MySQLdb.constants import FIELD_TYPE

def populate_database(dbase, content):
    """ Add new entries to the database with the given content """
    myquery  = " INSERT INTO Packages "
    myquery += "(package_id, build_id, rpm_id, srpm_id, build_name, "
    myquery += "nvr, Name, Version, Rel, "
    myquery += "Arch, URL, SRCRPM, DBGRPM, "
    myquery += "Vendor, BuiltBy, Category, Summary, "
    myquery += "Description, License, Date, Size) VALUES "
    myquery += "(%s, %s, %s, %s, \"%s\", " % (content['package_id'],
                                              content['build_id'],
                                              content['rpm_id'],
                                              content['srpm_id'],
                                              content['build_name'])
    myquery += "\"%s\", \"%s\", \"%s\", \"%s\", " % (content['nvr'],
                                                     content['Name'],
                                                     content['Version'],
                                                     content['Rel'])
    myquery += "\"%s\", \"%s\", \"%s\", \"%s\", " % (content['Arch'],
                                                     content['URL'],
                                                     content['SRCRPM'],
                                                     content['DBGRPM'])
    myquery += "\"%s\", \"%s\", \"%s\", \"%s\", " % (content['Vendor'],
                                                     content['BuiltBy'],
                                                     content['Category'],
                                                     content['Summary'])
    myquery += "\"%s\", \"%s\", %s, %s)" % (content['Description'],
                                            content['License'],
                                            content['Date'],
                                            content['Size'])
    dbase.query(myquery)
    for dep in content['dep_info']:
        if dep['type'] == 0:
            deptype = "Requires"
        elif dep['type'] == 1:
            deptype = "Provides"
        elif dep['type'] == 2:
            deptype = "Obsoletes"
        elif dep['type'] == 3:
            deptype = "Conflicts"

        depquery = """ INSERT INTO %s
        (rpm_id, Resource, Flags, Version, build_id) VALUES
        ( %s   , \"%s\"  , %s   , \"%s\" , %s)
        """ % (deptype, content['rpm_id'], dep['name'], dep['flags'],
               dep['version'], content['build_id'])
        try:
            dbase.query(depquery)
        except _mysql_exceptions.IntegrityError:
            pass

    for ifile in content['file_info']:
        filename = string.replace(ifile['name'], "\\", "\\\\")
        filequery = """ INSERT INTO Files
        (rpm_id, Path  , Flags, Digest, Size, build_id) VALUES
        (%s    , \"%s\", %s   , \"%s\", %s  , %s)
        """ % (content['rpm_id'], filename, ifile['flags'], ifile['digest'],
               ifile['size'], content['build_id'])
        # Maybe we have to use .encode('utf-8') on filenames.
        # Not necessary for now.
        try: # Normally, this shouldn't fail.
            dbase.query(filequery)
        except _mysql_exceptions.IntegrityError:
            # Here we can get "ProgrammingError"s due to weird file names. To
            # ignore this, we can replace the above line with
            # except (_mysql_exceptions.IntegrityError,
            #         _mysql_exceptions.ProgrammingError):
            pass

    for dist in content['dist_info']:
        distquery = """ INSERT INTO Distribution
        (rpm_id, repo, build_id) VALUES
        (%s    ,\"%s\", %s)
        """ % (content['rpm_id'], dist, content['build_id'])
        dbase.query(distquery)

    for entry in content['specchangelog']:
        entry['author'] = entry['author'].encode('utf-8')
        entry['text'] = entry['text'].encode('utf-8')
        dbase.execute(""" INSERT INTO SpecChangeLogs
                (build_id, Date, Author, Text, rpm_id)
                VALUES (%s      , %s  , "%s"  , "%s", %s)""", 
            (content['build_id'], entry['date_ts'], entry['author'],
               entry['text'], content['rpm_id']) )

    # Sanitization
    if content['softwarechangelog']:
        content['softwarechangelog'] = string.replace(
            content['softwarechangelog'], "\\", "\\\\")
        content['softwarechangelog'] = string.replace(
            content['softwarechangelog'], '"', '\\\"')
        content['softwarechangelog'] = string.replace(
            content['softwarechangelog'], "'", "\\\'")
        try:
            content['softwarechangelog'] = content[
                'softwarechangelog'].encode('utf-8')
        except UnicodeDecodeError:
            pass
        softwareclogquery = """ INSERT INTO SoftwareChangeLogs
        (build_id, Filename, Text) VALUES
        (%s      , "%s"    , "%s")
        """ % (content['build_id'], content['softwarechangelogfile'],
               content['softwarechangelog'])

        dbase.query(softwareclogquery)

def remove_old(app, kojisession, dbase):
    """ Delete package entries from database """
    all_distvers = app.config.get("repositories", "alldistvers").split()
    all_releases = app.config.get("repositories", "allreleases").split()
    relver = app.distver
    relname = app.config.get("repositories", "distname")

    # Gets the RPM release based on what distribution version we're using
    for rel in zip(all_distvers, all_releases):
        if int(relver) == int(rel(0)):
            release = rel(1)
            selection_query = "select distinct build_id from Packages where Rel=" + release
            break
    else:
        app.logger.warning("Release not found while removing old packages.")
        app.logger.warning("Reverting to old behavior: all matching packages from all releases will be removed.")
        selection_query = "select distinct build_id from Packages"

    # We only want packages for our current distver
    dbase.query(selection_query)
    try:
        res = dbase.store_result()
    except e:
        app.logger.warning(e.message)
    dat = res.fetch_row(maxrows=0)
    build_ids_in_db = []
    for entry in dat:
        build_ids_in_db.append(entry[0])
    latest_builds = []

    repo_prefix = relname + relver + "-"
    repos = app.config.get("repositories", "allrepos").split()
    for i, r in enumerate(repos[:]):
        repos[i] = repo_prefix + r

    for repo in repos:
        latest_builds += kojisession.getLatestBuilds(repo)
    build_ids_in_repo = []
    for build in latest_builds:
        build_ids_in_repo.append(build['build_id'])
    for build_id in build_ids_in_db:
        if not build_id in build_ids_in_repo:
            List_query = """ SELECT nvr, arch FROM Packages WHERE
            build_id = %s
            """ % (build_id)
            dbase.query(List_query)
            res = dbase.store_result()
            rpms2remove = res.fetch_row(maxrows=0)

            for table in ['Packages', 'Distribution', 'Files', 'Requires',
                          'Provides', 'Obsoletes', 'Conflicts',
                          'SpecChangeLogs', 'SoftwareChangeLogs']:
                Packages_query = """ delete from %s where
                build_id = %s
                """ % (table, build_id)
                dbase.query(Packages_query)
            for nvr in rpms2remove:
                app.logger.info("Package: " + nvr[0] + "." + nvr[1] +
                                " removed from database.")


def fetch_repo(app, kojisession, dbase):
    """ Get latests builds from koji and process their information.
    Then trigger populate_database(database, information)"""
    dbase.query("SELECT DISTINCT build_id FROM Packages")
    res = dbase.store_result()
    dat = res.fetch_row(maxrows=0)
    build_ids_in_db = []
    for entry in dat:
        build_ids_in_db.append(entry[0])

    latest_builds = []

    relver = app.distver
    relname = app.config.get("repositories", "distname")
    repo_prefix = relname + relver + "-"
    repos = app.config.get("repositories", "allrepos").split()
    for i in range(len(repos)):
        repos[i] = repo_prefix + repos[i]

    for repo in repos:
        latest_builds += kojisession.getLatestBuilds(repo)
    for build in latest_builds:
        build_id = build['build_id']
        if build_id == 2010:
            print build
        tags = kojisession.listTags(build_id)
        dist_info = []
        for tag in tags:
            dist_info.append(tag['name'])

        if build_id in build_ids_in_db:
            tagquery  = "SELECT DISTINCT repo FROM Distribution WHERE build_id="
            tagquery += str(build_id)
            dbase.query(tagquery)
            res = dbase.store_result()
            dat = res.fetch_row(maxrows=0)
            tags_in_db = []
            for entry in dat:
                tags_in_db.append(entry[0])
            for tag in dist_info:
                if not tag in tags_in_db:
                    build_rpms = kojisession.listBuildRPMs(build_id)
                    for rpm in build_rpms:
                        #if (rpm['arch'] != 'src' and
                        #    not rpm['name'].endswith('-debuginfo')):
                        if not rpm['name'].endswith('-debuginfo'):
                            newtagquery = """ INSERT INTO Distribution
                            (rpm_id, repo, build_id) VALUES
                            (%s    ,"%s", %s)
                            """ % (rpm['id'], tag, build_id)
                            app.logger.info("New tag: " + tag + \
                                            " for package: " + rpm['nvr'] + \
                                            "." + rpm['arch'])
                            dbase.query(newtagquery)
            for tag in tags_in_db: # Reverse check
                if not tag in dist_info:
                    build_rpms = kojisession.listBuildRPMs(build_id)
                    for rpm in build_rpms:
                        #if (rpm['arch'] != 'src' and
                        #    not rpm['name'].endswith('-debuginfo')):
                        if not rpm['name'].endswith('-debuginfo'):
                            removetagquery = """ DELETE FROM Distribution WHERE
                            rpm_id = %s AND repo = "%s"
                            """ % (rpm['id'], tag)
                            app.logger.info("Tag: " + tag +
                                            " removed from package: " +
                                            rpm['nvr'] + "." + rpm['arch'])
                            dbase.query(removetagquery)
        else:
            build_ids_in_db.append(build_id)

            build_name = build['name']
            package_id = build['package_id']
            built_by = build['owner_name']
            build_rpms = kojisession.listBuildRPMs(build_id)
            build_nvr = ""
            srpm_id = None
            pkgdir = app.config.get("koji", "pkgdir")
            build_dbg = None
            build_sw_clog = None
            for rpm in build_rpms:
                if rpm['arch'] == 'src':
                    build_nvr = rpm['nvr']
                    srpm_id = rpm['id']
                elif rpm['name'].endswith('-debuginfo'):
                    build_dbg = rpm['nvr']
            for rpm in build_rpms:
                #if (rpm['arch'] != 'src' and
                #    not rpm['name'].endswith('-debuginfo')):
                if not rpm['name'].endswith('-debuginfo'):
                    rpminfo = {}
                    rpminfo['build_id'] = build_id
                    rpminfo['package_id'] = package_id
                    rpminfo['rpm_id'] = rpm['id']
                    rpminfo['srpm_id'] = srpm_id
                    rpminfo['build_name'] = build_name
                    rpminfo['BuiltBy'] = built_by
                    rpminfo['dist_info'] = dist_info
                    rpminfo['nvr'] = rpm['nvr']
                    rpminfo['Name'] = rpm['name']
                    rpminfo['Version'] = rpm['version']
                    rpminfo['Rel'] = rpm['release']
                    rpminfo['Arch'] = rpm['arch']
                    rpminfo['Size'] = rpm['size']
                    rpminfo['Date'] = rpm['buildtime']
                    rpminfo['SRCRPM'] = build_nvr + '.src.rpm'
                    if build_dbg and rpm['arch'] != 'noarch':
                        rpminfo['DBGRPM'] = build_dbg
                    else:
                        rpminfo['DBGRPM'] = None

                    headers = ['description', 'summary', 'group',
                               'vendor', 'url', 'license']
                    harray = kojisession.getRPMHeaders(rpmID=rpm['id'],
                                                       headers=headers)
                    rpminfo['URL'] = harray['url']
                    rpminfo['Vendor'] = harray['vendor']
                    rpminfo['Category'] = harray['group']
                    rpminfo['Summary'] = string.replace(
                        harray['summary'], '"', '\\\"').encode('utf-8')
                    rpminfo['Description'] = string.replace(
                        harray['description'], '"', '\\\"').encode('utf-8')
                    rpminfo['License'] = harray['license']

                    rpminfo['dep_info'] = kojisession.getRPMDeps(rpm['id'])
                    rpminfo['file_info'] = kojisession.listRPMFiles(rpm['id'])
                    rpminfo['specchangelog'] = kojisession.getChangelogEntries(build_id)

                    rpm_filepath = pkgdir + "/" + rpminfo['build_name'] + \
                                   "/" + build['version'] + "/" + \
                                   build['release'] + "/" + rpm['arch'] + \
                                   "/" + rpm['name'] + "-" + rpm['version'] + \
                                   "-" + rpm['release'] + "." + rpm['arch'] + \
                                   ".rpm"
                    rpminfo['softwarechangelog'] = ""
                    rpminfo['softwarechangelogfile'] = ""
                    if not build_sw_clog:
                        cloginfo = get_software_clog(rpm_filepath)
                        if cloginfo:
                            rpminfo['softwarechangelogfile'] = cloginfo[0]
                            rpminfo['softwarechangelog'] = cloginfo[1]
                    if rpminfo['softwarechangelogfile']:
                        build_sw_clog = True

                    app.logger.info(rpminfo['nvr'] + "." + rpminfo['Arch'] +
                                    " with rpm_id " + str(rpm['id']) +
                                    " entered to the database.")
                    populate_database(dbase, rpminfo)

def get_software_clog(rpmfile):
    """ Search the RPMs with a given build ID for a ChangeLog file.
    Retrieve its contents."""
    filelist_command = "rpm2cpio " + rpmfile  + " | cpio -t --quiet"
    aout = os.popen(filelist_command)
    filelist = aout.readlines()
    aout.close()

    clogfile = None
    cloglist = ["changeLog", "Changes", "NEWS"]
    for ifile in filelist:
        if not "/usr/share/doc" in ifile:
            continue
        for clogcandidate in cloglist:
            if string.lower(clogcandidate) == string.lower(
                ifile[string.rfind(ifile, "/")+1:]):
                clogfile = ifile[:-1]
                break

        if not clogfile:
            for clogcandidate in cloglist:
                if string.lower(clogcandidate) in string.lower(ifile):
                    clogfile = ifile[:-1]
                    break

        if clogfile:
            break

    if clogfile:
        clog_command = "rpm2cpio " + rpmfile + \
                       " | cpio -i --to-stdout --quiet " + clogfile
        aout = os.popen(clog_command)
        swclog = aout.readlines()
        aout.close()
        #print clogfile, string.join(swclog)
        return [clogfile[1:], string.join(swclog)]

    return False

def clean_database(app, dbase):
    """ Empty the database """
    dropquery = []
    dropquery.append("DROP TABLES IF EXISTS ChangeLogs, Conflicts, ")
    dropquery.append("Distribution, Files, Obsoletes, Packages, Provides, ")
    dropquery.append("Requires, SoftwareChangeLogs, SpecChangeLogs;")

    dbase.query("".join(dropquery))
    app.logger.info("Tables removed from the database")

def create_tables(app, dbase):
    """ Create a database with empty tables to be filled """
    Packages_query = """CREATE TABLE IF NOT EXISTS Packages
    (package_id int(11) not null, build_id int(11) not null, rpm_id int(11),
    srpm_id int(11),
    PRIMARY KEY(rpm_id), build_name varchar(50) not null,
    nvr varchar(255) not null, Name varchar(50) not null,
    Version varchar(50) not null, Rel varchar(50) not null,
    Arch varchar(15) not null, URL varchar(255), SRCRPM varchar(255) not null,
    DBGRPM varchar(255), Vendor varchar(50), BuiltBy varchar(20) not null,
    Category varchar(255) not null, Summary varchar(255), Description text,
    License varchar(255), Date int(11) not null, Size int(11) not null)"""
    dbase.query(Packages_query)
    Files_query = """CREATE TABLE IF NOT EXISTS Files (rpm_id int(11),
    Path varchar(255), PRIMARY KEY(rpm_id, Path), Flags int(31),
    Size int(11) not null, Digest varchar(31), build_id int(11) not null)"""
    dbase.query(Files_query)
    Requires_query = """CREATE TABLE IF NOT EXISTS Requires (rpm_id int(11),
    Resource varchar(50), PRIMARY KEY(rpm_id, Resource), Flags int(31),
    Version varchar(20), build_id int(11) not null)"""
    dbase.query(Requires_query)
    Provides_query = """CREATE TABLE IF NOT EXISTS Provides (rpm_id int(11),
    Resource varchar(50), PRIMARY KEY(rpm_id, Resource), Flags int(31),
    Version varchar(20), build_id int(11) not null)"""
    dbase.query(Provides_query)
    Obsoletes_query = """CREATE TABLE IF NOT EXISTS Obsoletes (rpm_id int(11),
    Resource varchar(50), PRIMARY KEY(rpm_id, Resource), Flags int(31),
    Version varchar(20), build_id int(11) not null)"""
    dbase.query(Obsoletes_query)
    Conflicts_query = """CREATE TABLE IF NOT EXISTS Conflicts (rpm_id int(11),
    Resource varchar(50), PRIMARY KEY(rpm_id, Resource), Flags int(31),
    Version varchar(20), build_id int(11) not null)"""
    dbase.query(Conflicts_query)
    Distribution_query = """CREATE TABLE IF NOT EXISTS Distribution
    (rpm_id int(11), repo varchar(50), PRIMARY KEY(rpm_id, repo),
    build_id int(11) not null)"""
    dbase.query(Distribution_query)
    SpecChangeLogs_query = """CREATE TABLE IF NOT EXISTS SpecChangeLogs
    (ID int(15) AUTO_INCREMENT, build_id int(11), Date int(11),
    Author varchar(255), PRIMARY KEY(ID), Text text, rpm_id int(11))"""
    dbase.query(SpecChangeLogs_query)
    SoftwareChangeLogs_query = """CREATE TABLE IF NOT EXISTS SoftwareChangeLogs
    (build_id int(11), PRIMARY KEY(build_id), Filename varchar(255),
    Text text)"""
    dbase.query(SoftwareChangeLogs_query)
    SpecChangeLogs_query = """CREATE TABLE IF NOT EXISTS SpecChangeLogs (ID
    int(15) AUTO_INCREMENT, build_id int(11), Date int(11),
    Author varchar(255), PRIMARY KEY(ID), Text text, rpm_id int (11));"""
    dbase.query(SpecChangeLogs_query)

    app.logger.info("Tables Created (if they didn't exist)")


def update_db(app, clean=False, create=False, removeoldpkg=False):
    """ Wrapper function that governs everything """
    my_conv = { FIELD_TYPE.LONG: int }
    db_host = app.config.get("rpmdb", "host")
    db_user = app.config.get("rpmdb", "user")
    db_pw   = app.config.get("rpmdb", "password")
    db_name = app.config.get("rpmdb", "name")

    dbase = _mysql.connect(db_host, db_user, db_pw, db_name, conv=my_conv)

    kojisession = app.get_koji_session(ssl = False)

    if clean:
        clean_database(app, dbase)
    if create:
        create_tables(app, dbase)
    if removeoldpkg:
        remove_old(app, kojisession, dbase)
    fetch_repo(app, kojisession, dbase)

    dbase.close()
