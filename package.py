from app.models import Cent6Packages

class PackageName():
    def __init__(self, name, packages):
        self.name = name
        self.packages = packages
        self.archs = []
        self.repos = {'stable': ['centos5-rutgers', 'centos6-rutgers'], 'testing': ['centos5-rutgers-testing', 'centos6-rutgers-testing'], 'unstable': ['centos5-rutgers-unstable', 'centos6-rutgers-unstable']}
        for package in self.packages:
            if package.Arch not in self.archs:
                self.archs.append(package.Arch)
        self.newest = {}
        for repotype in self.repos.keys():
            for repo in self.repos[repotype]:
                self.newest[repo] = self.newestversion(repo)
            
    def newestversion(self, repo):
        newest = None
        date = 0
        for package in self.packages:
            for distribution in package.distributions:
                if package.Date > date and distribution.repo == repo:
                    newest = package
                    date = package.Date
        if date == 0:
            newest = Cent6Packages()
            newest.Version = ""
            newest.Rel = ""
        return newest
