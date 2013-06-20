from app import db1, db2

class Cent6ChangeLogs(db1.Model):
    __tablename__ = 'ChangeLogs'
    __bind_key__ = 'cent6'
    ID = db1.Column(db1.Integer, primary_key=True, nullable=False, autoincrement=True)
    build_id = db1.Column(db1.Integer)
    Date = db1.Column(db1.Integer)
    Author = db1.Column(db1.String(255))
    Text = db1.Column(db1.Text)
    rpm_id = db1.Column(db1.Integer, db1.ForeignKey('Packages.rpm_id'))

class Cent6Conflicts(db1.Model):
    __tablename__ = 'Conflicts'
    __bind_key__ = 'cent6'
    rpm_id = db1.Column(db1.Integer, db1.ForeignKey('Packages.rpm_id'), nullable=False, primary_key=True, default=0)
    Resource = db1.Column(db1.String(50), nullable=False, primary_key=True)
    Flags = db1.Column(db1.Integer)
    Version = db1.Column(db1.String(20))
    build_id = db1.Column(db1.Integer, nullable=False)

class Cent6Distribution(db1.Model):
    __tablename__ = 'Distribution'
    __bind_key__ = 'cent6'
    rpm_id = db1.Column(db1.Integer, db1.ForeignKey('Packages.rpm_id'), nullable=False, primary_key=True, default=0)
    repo = db1.Column(db1.String(50), nullable=False, primary_key=True)
    build_id = db1.Column(db1.Integer, nullable=False)

class Cent6Files(db1.Model):
    __tablename__ = 'Files'
    __bind_key__ = 'cent6'
    rpm_id = db1.Column(db1.Integer, db1.ForeignKey('Packages.rpm_id'), nullable=False, primary_key=True, default=0)
    Path = db1.Column(db1.String(255), nullable=False, primary_key=True)
    Flags = db1.Column(db1.Integer)
    Size = db1.Column(db1.Integer, nullable=False)
    Digest = db1.Column(db1.String(31))
    build_id = db1.Column(db1.Integer, nullable=False)

class Cent6Obsoletes(db1.Model):
    __tablename__ = 'Obsoletes'
    __bind_key__ = 'cent6'
    rpm_id = db1.Column(db1.Integer, db1.ForeignKey('Packages.rpm_id'), nullable=False, primary_key=True, default=0)
    Resource = db1.Column(db1.String(50), nullable=False, primary_key=True)
    Flags = db1.Column(db1.Integer)
    Version = db1.Column(db1.String(20))
    build_id = db1.Column(db1.Integer, nullable=False)

class Cent6Packages(db1.Model):
    __tablename__ = 'Packages'
    __bind_key__ = 'cent6'
    package_id = db1.Column(db1.Integer, nullable=False)
    build_id = db1.Column(db1.Integer, nullable=False)
    rpm_id = db1.Column(db1.Integer, nullable=False, primary_key=True, default=0)
    srpm_id = db1.Column(db1.Integer)
    build_name = db1.Column(db1.String(50), nullable=False)
    nvr = db1.Column(db1.String(255), nullable=False)
    Name = db1.Column(db1.String(50), nullable=False)
    Version = db1.Column(db1.String(50), nullable=False)
    Rel = db1.Column(db1.String(50), nullable=False)
    Arch = db1.Column(db1.String(15), nullable=False)
    URL = db1.Column(db1.String(255))
    SRCRPM = db1.Column(db1.String(255), nullable=False)
    DBGRPM = db1.Column(db1.String(255))
    Vendor = db1.Column(db1.String(50))
    BuiltBy = db1.Column(db1.String(20), nullable=False)
    Category = db1.Column(db1.String(255), nullable=False)
    Summary = db1.Column(db1.String(255))
    Description = db1.Column(db1.Text)
    License = db1.Column(db1.String(255))
    Date = db1.Column(db1.Integer, nullable=False)
    Size = db1.Column(db1.Integer, nullable=False)
    changelog = db1.relationship('Cent6ChangeLogs', backref='package', lazy='dynamic')
    conflicts = db1.relationship('Cent6Conflicts', backref='package', lazy='dynamic')
    distributions = db1.relationship('Cent6Distribution', backref='package', lazy='dynamic')
    files = db1.relationship('Cent6Files', backref='package', lazy='dynamic')
    obsoletes = db1.relationship('Cent6Obsoletes', backref='package', lazy='dynamic')
    provides = db1.relationship('Cent6Provides', backref='package', lazy='dynamic')
    requires = db1.relationship('Cent6Requires', backref='package', lazy='dynamic')
    softwarechangelogs = db1.relationship('Cent6SoftwareChangeLogs', backref='package', uselist=False)
    specchangelogs = db1.relationship('Cent6SpecChangeLogs', backref='package', lazy='dynamic')

class Cent6Provides(db1.Model):
    __tablename__ = 'Provides'
    __bind_key__ = 'cent6'
    rpm_id = db1.Column(db1.Integer, db1.ForeignKey('Packages.rpm_id'), nullable=False, primary_key=True, default=0)
    Resource = db1.Column(db1.String(50), nullable=False, primary_key=True)
    Flags = db1.Column(db1.Integer)
    Version = db1.Column(db1.String(20))
    build_id = db1.Column(db1.Integer, nullable=False)

class Cent6Requires(db1.Model):
    __tablename__ = 'Requires'
    __bind_key__ = 'cent6'
    rpm_id = db1.Column(db1.Integer, db1.ForeignKey('Packages.rpm_id'), nullable=False, primary_key=True, default=0)
    Resource = db1.Column(db1.String(50), nullable=False, primary_key=True)
    Flags = db1.Column(db1.Integer)
    Version = db1.Column(db1.String(20))
    build_id = db1.Column(db1.Integer, nullable=False)

class Cent6SoftwareChangeLogs(db1.Model):
    __tablename__ = 'SoftwareChangeLogs'
    __bind_key__ = 'cent6'
    build_id = db1.Column(db1.Integer, db1.ForeignKey('Packages.build_id'), nullable=False, primary_key=True, default=0)
    Filename = db1.Column(db1.String(255))
    Text = db1.Column(db1.Text)

class Cent6SpecChangeLogs(db1.Model):
    __tablename__ = 'SpecChangeLogs'
    __bind_key__ = 'cent6'
    ID = db1.Column(db1.Integer, nullable=False, primary_key=True, autoincrement=True)
    build_id = db1.Column(db1.Integer)
    Date = db1.Column(db1.Integer)
    Author = db1.Column(db1.String(255))
    Text = db1.Column(db1.Text)
    rpm_id = db1.Column(db1.Integer, db1.ForeignKey('Packages.rpm_id'))

class Cent5ChangeLogs(db2.Model):
    __tablename__ = 'ChangeLogs'
    __bind_key__ = 'cent5'
    ID = db2.Column(db2.Integer, primary_key=True, nullable=False, autoincrement=True)
    build_id = db2.Column(db2.Integer)
    Date = db2.Column(db2.Integer)
    Author = db2.Column(db2.String(255))
    Text = db2.Column(db2.Text)
    rpm_id = db2.Column(db2.Integer, db2.ForeignKey('Packages.rpm_id'))

class Cent5Conflicts(db2.Model):
    __tablename__ = 'Conflicts'
    __bind_key__ = 'cent5'
    rpm_id = db2.Column(db2.Integer, db2.ForeignKey('Packages.rpm_id'), nullable=False, primary_key=True, default=0)
    Resource = db2.Column(db2.String(50), nullable=False, primary_key=True)
    Flags = db2.Column(db2.Integer)
    Version = db2.Column(db2.String(20))
    build_id = db2.Column(db2.Integer, nullable=False)

class Cent5Distribution(db2.Model):
    __tablename__ = 'Distribution'
    __bind_key__ = 'cent5'
    rpm_id = db2.Column(db2.Integer, db2.ForeignKey('Packages.rpm_id'), nullable=False, primary_key=True, default=0)
    repo = db2.Column(db2.String(50), nullable=False, primary_key=True)
    build_id = db2.Column(db2.Integer, nullable=False)

class Cent5Files(db2.Model):
    __tablename__ = 'Files'
    __bind_key__ = 'cent5'
    rpm_id = db2.Column(db2.Integer, db2.ForeignKey('Packages.rpm_id'), nullable=False, primary_key=True, default=0)
    Path = db2.Column(db2.String(255), nullable=False, primary_key=True)
    Flags = db2.Column(db2.Integer)
    Size = db2.Column(db2.Integer, nullable=False)
    Digest = db2.Column(db2.String(31))
    build_id = db2.Column(db2.Integer, nullable=False)

class Cent5Obsoletes(db2.Model):
    __tablename__ = 'Obsoletes'
    __bind_key__ = 'cent5'
    rpm_id = db2.Column(db2.Integer, db2.ForeignKey('Packages.rpm_id'), nullable=False, primary_key=True, default=0)
    Resource = db2.Column(db2.String(50), nullable=False, primary_key=True)
    Flags = db2.Column(db2.Integer)
    Version = db2.Column(db2.String(20))
    build_id = db2.Column(db2.Integer, nullable=False)

class Cent5Packages(db2.Model):
    __tablename__ = 'Packages'
    __bind_key__ = 'cent5'
    package_id = db2.Column(db2.Integer, nullable=False)
    build_id = db2.Column(db2.Integer, nullable=False)
    rpm_id = db2.Column(db2.Integer, nullable=False, primary_key=True, default=0)
    srpm_id = db2.Column(db2.Integer)
    build_name = db2.Column(db2.String(50), nullable=False)
    nvr = db2.Column(db2.String(255), nullable=False)
    Name = db2.Column(db2.String(50), nullable=False)
    Version = db2.Column(db2.String(50), nullable=False)
    Rel = db2.Column(db2.String(50), nullable=False)
    Arch = db2.Column(db2.String(15), nullable=False)
    URL = db2.Column(db2.String(255))
    SRCRPM = db2.Column(db2.String(255), nullable=False)
    DBGRPM = db2.Column(db2.String(255))
    Vendor = db2.Column(db2.String(50))
    BuiltBy = db2.Column(db2.String(20), nullable=False)
    Category = db2.Column(db2.String(255), nullable=False)
    Summary = db2.Column(db2.String(255))
    Description = db2.Column(db2.Text)
    License = db2.Column(db2.String(255))
    Date = db2.Column(db2.Integer, nullable=False)
    Size = db2.Column(db2.Integer, nullable=False)
    changelog = db2.relationship('Cent5ChangeLogs', backref='package', lazy='dynamic')
    conflicts = db2.relationship('Cent5Conflicts', backref='package', lazy='dynamic')
    distributions = db2.relationship('Cent5Distribution', backref='package', lazy='dynamic')
    files = db2.relationship('Cent5Files', backref='package', lazy='dynamic')
    obsoletes = db2.relationship('Cent5Obsoletes', backref='package', lazy='dynamic')
    provides = db2.relationship('Cent5Provides', backref='package', lazy='dynamic')
    requires = db2.relationship('Cent5Requires', backref='package', lazy='dynamic')
    softwarechangelogs = db2.relationship('Cent5SoftwareChangeLogs', backref='package', uselist=False)
    specchangelogs = db2.relationship('Cent5SpecChangeLogs', backref='package', lazy='dynamic')

class Cent5Provides(db2.Model):
    __tablename__ = 'Provides'
    __bind_key__ = 'cent5'
    rpm_id = db2.Column(db2.Integer, db2.ForeignKey('Packages.rpm_id'), nullable=False, primary_key=True, default=0)
    Resource = db2.Column(db2.String(50), nullable=False, primary_key=True)
    Flags = db2.Column(db2.Integer)
    Version = db2.Column(db2.String(20))
    build_id = db2.Column(db2.Integer, nullable=False)

class Cent5Requires(db2.Model):
    __tablename__ = 'Requires'
    __bind_key__ = 'cent5'
    rpm_id = db2.Column(db2.Integer, db2.ForeignKey('Packages.rpm_id'), nullable=False, primary_key=True, default=0)
    Resource = db2.Column(db2.String(50), nullable=False, primary_key=True)
    Flags = db2.Column(db2.Integer)
    Version = db2.Column(db2.String(20))
    build_id = db2.Column(db2.Integer, nullable=False)

class Cent5SoftwareChangeLogs(db2.Model):
    __tablename__ = 'SoftwareChangeLogs'
    __bind_key__ = 'cent5'
    build_id = db2.Column(db2.Integer, db2.ForeignKey('Packages.build_id'), nullable=False, primary_key=True, default=0)
    Filename = db2.Column(db2.String(255))
    Text = db2.Column(db2.Text)

class Cent5SpecChangeLogs(db2.Model):
    __tablename__ = 'SpecChangeLogs'
    __bind_key__ = 'cent5'
    ID = db2.Column(db2.Integer, nullable=False, primary_key=True, autoincrement=True)
    build_id = db2.Column(db2.Integer)
    Date = db2.Column(db2.Integer)
    Author = db2.Column(db2.String(255))
    Text = db2.Column(db2.Text)
    rpm_id = db2.Column(db2.Integer, db2.ForeignKey('Packages.rpm_id'))
