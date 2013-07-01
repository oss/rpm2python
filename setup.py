from distutils.core import setup

setup(
    name = 'rpm2python',
    version = '1.0.2',
    description = 'Web interface for Rutgers package database',
    author = 'Matt Robinson',
    author_email = 'oss@oss.rutgers.edu',
    url = 'https://github.com/mrobinson7627/rpm2python',
    license = 'BSD',
    platforms = ['linux'],
    long_description =   '''rpm2python queries the database and displays information about the latest
                            version of each package in each repo. It supports full text search for
                            several different package qualities including name and dependancies''',
    packages = ['rpm2python'],
    include_package_data = True,
    zip_safe=False,
    install_reqires = [
        'Flask==0.10.1',
        'Flask=SQLALchemy==0.16',
        'Flask-WTF==0.8.3',
        'MySQL-python==1.2.4'
    ]
)
