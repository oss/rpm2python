from app.models import Cent6Packages, Cent5Packages

#PackageName is used in the index template for ordering purposes
#it groups packages of the same name together, and gets the latest version
#from each repo to display it
class PackageName():
    def __init__(self, name, packages):
        self.name = name
        self.packages = packages
        self.archs = []
        self.repos = {
                'stable': ['centos5-rutgers', 'centos6-rutgers'],
                'testing': ['centos5-rutgers-testing', 'centos6-rutgers-testing'],
                'unstable': ['centos5-rutgers-unstable', 'centos6-rutgers-unstable']}
        fakepack = Cent6Packages()
        fakepack.Version = ""
        fakepack.Rel = ""
        self.newest = {}
        for genrepo in self.repos:
            for repo in self.repos[genrepo]:
                self.newest[repo] = fakepack
        for package in self.packages:
            self.newest[package[1]] = package[0]
        duparchs = Cent6Packages.query.filter_by(Name=name).all()
        duparchs.extend(Cent5Packages.query.filter_by(Name=name).all())
        for arch in duparchs:
            if arch.Arch not in self.archs:
                self.archs.append(arch.Arch)
