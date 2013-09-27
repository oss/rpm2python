'''
These classes for models for all the tables in the database.
Cent5 and 6 are identical, but because of a limitation in SQLAlchemy
there is no way to have them in the same metadata instance,
or even inherit from the same base class.
They are nearly identical except for references to Cent5 are Cent6
in each class, and db2 is used in Cent5 and db in Cent6.
The binds are also different and can
be changed in the config file

If you can find a better way to do this, PLEASE change it!

Each class is pretty much a description of the table it shares a
name with. Take a look inside the database if you want to know more
about what each are for.
'''
from rpm2python import db


class ChangeLogs(db.Model):
    __tablename__ = 'ChangeLogs'
    ID = db.Column(db.Integer, primary_key=True,
                    nullable=False, autoincrement=True)
    build_id = db.Column(db.Integer)
    Date = db.Column(db.Integer)
    Author = db.Column(db.String(255))
    Text = db.Column(db.Text)
    rpm_id = db.Column(db.Integer, db.ForeignKey('Packages.rpm_id'))


class Conflicts(db.Model):
    __tablename__ = 'Conflicts'
    rpm_id = db.Column(db.Integer,
                        db.ForeignKey('Packages.rpm_id'),
                        nullable=False, primary_key=True, default=0)
    Resource = db.Column(db.String(50), nullable=False, primary_key=True)
    Flags = db.Column(db.Integer)
    Version = db.Column(db.String(20))
    build_id = db.Column(db.Integer, nullable=False)


class Distribution(db.Model):
    __tablename__ = 'Distribution'
    rpm_id = db.Column(db.Integer,
                        db.ForeignKey('Packages.rpm_id'),
                        nullable=False, primary_key=True, default=0)
    repo = db.Column(db.String(50), nullable=False, primary_key=True)
    build_id = db.Column(db.Integer, nullable=False)


class Files(db.Model):
    __tablename__ = 'Files'
    rpm_id = db.Column(db.Integer,
                        db.ForeignKey('Packages.rpm_id'),
                        nullable=False, primary_key=True, default=0)
    Path = db.Column(db.String(255), nullable=False, primary_key=True)
    Flags = db.Column(db.Integer)
    Size = db.Column(db.Integer, nullable=False)
    Digest = db.Column(db.String(31))
    build_id = db.Column(db.Integer, nullable=False)


class Obsoletes(db.Model):
    __tablename__ = 'Obsoletes'
    rpm_id = db.Column(db.Integer,
                        db.ForeignKey('Packages.rpm_id'),
                        nullable=False, primary_key=True, default=0)
    Resource = db.Column(db.String(50), nullable=False, primary_key=True)
    Flags = db.Column(db.Integer)
    Version = db.Column(db.String(20))
    build_id = db.Column(db.Integer, nullable=False)


class Packages(db.Model):
    __tablename__ = 'Packages'
    package_id = db.Column(db.Integer, nullable=False)
    build_id = db.Column(db.Integer, nullable=False)
    rpm_id = db.Column(db.Integer,
                        nullable=False, primary_key=True, default=0)
    srpm_id = db.Column(db.Integer)
    build_name = db.Column(db.String(50), nullable=False)
    nvr = db.Column(db.String(255), nullable=False)
    Name = db.Column(db.String(50), nullable=False)
    Version = db.Column(db.String(50), nullable=False)
    Rel = db.Column(db.String(50), nullable=False)
    Arch = db.Column(db.String(15), nullable=False)
    URL = db.Column(db.String(255))
    SRCRPM = db.Column(db.String(255), nullable=False)
    DBGRPM = db.Column(db.String(255))
    Vendor = db.Column(db.String(50))
    BuiltBy = db.Column(db.String(20), nullable=False)
    Category = db.Column(db.String(255), nullable=False)
    Summary = db.Column(db.String(255))
    Description = db.Column(db.Text)
    License = db.Column(db.String(255))
    Date = db.Column(db.Integer, nullable=False)
    Size = db.Column(db.Integer, nullable=False)
    changelog = db.relationship('ChangeLogs',
                                backref='package',
                                lazy='dynamic')
    conflicts = db.relationship('Conflicts',
                                backref='package',
                                lazy='dynamic')
    distributions = db.relationship('Distribution',
                                    backref='package',
                                    lazy='dynamic')
    files = db.relationship('Files',
                            backref='package',
                            lazy='dynamic')
    obsoletes = db.relationship('Obsoletes',
                                backref='package',
                                lazy='dynamic')
    provides = db.relationship('Provides',
                                backref='package',
                                lazy='dynamic')
    requires = db.relationship('Requires',
                                backref='package',
                                lazy='dynamic')
    softwarechangelogs = db.relationship('SoftwareChangeLogs',
                                        backref='package',
                                        uselist=False)
    specchangelogs = db.relationship('SpecChangeLogs',
                                    order_by="SpecChangeLogs.ID",
                                    backref='package',
                                    lazy='dynamic')

class Provides(db.Model):
    __tablename__ = 'Provides'
    rpm_id = db.Column(db.Integer,
                        db.ForeignKey('Packages.rpm_id'),
                        nullable=False, primary_key=True, default=0)
    Resource = db.Column(db.String(50), nullable=False, primary_key=True)
    Flags = db.Column(db.Integer)
    Version = db.Column(db.String(20))
    build_id = db.Column(db.Integer, nullable=False)


class Requires(db.Model):
    __tablename__ = 'Requires'
    rpm_id = db.Column(db.Integer,
                        db.ForeignKey('Packages.rpm_id'),
                        nullable=False, primary_key=True, default=0)
    Resource = db.Column(db.String(50), nullable=False, primary_key=True)
    Flags = db.Column(db.Integer)
    Version = db.Column(db.String(20))
    build_id = db.Column(db.Integer, nullable=False)


class SoftwareChangeLogs(db.Model):
    __tablename__ = 'SoftwareChangeLogs'
    build_id = db.Column(db.Integer,
                            db.ForeignKey('Packages.build_id'),
                            nullable=False, primary_key=True, default=0)
    Filename = db.Column(db.String(255))
    Text = db.Column(db.Text)


class SpecChangeLogs(db.Model):
    __tablename__ = 'SpecChangeLogs'
    ID = db.Column(db.Integer,
                    nullable=False, primary_key=True, autoincrement=True)
    build_id = db.Column(db.Integer)
    Date = db.Column(db.Integer)
    Author = db.Column(db.String(255))
    Text = db.Column(db.Text)
    rpm_id = db.Column(db.Integer, db.ForeignKey('Packages.rpm_id'))
