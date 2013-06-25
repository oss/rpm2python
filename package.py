from app.models import Cent6Packages

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
            if package[0].Arch not in self.archs:
                self.archs.append(package[0].Arch)
            self.newest[package[1]] = package[0]
