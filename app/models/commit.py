import subprocess, shutil, os
from ..util.cache_folder import CacheFolder
from ..flask_shared import app
from .library import Library
from ..util.lock_pool import shared_lock

class Commit:
    def __init__(self, repository, id, mc):
        self.repository = repository
        self.id = id
        self.mc = mc
        self.path = CacheFolder().get_path("ref_" + self.id)

    def clean_up(self):
        shutil.rmtree(self.path, ignore_errors=True)

    def fetch(self):
        with shared_lock('commit_%s' % self.id):
            if not os.path.isdir(self.path):
                app.logger.info("Checking out %s from repository %s" % (self.id, self.repository.url))
                shutil.copytree(self.repository.path, self.path)
                result = self.run(["git", 'checkout', self.id])
                if result.returncode > 0:
                    print(result)
                    raise Exception("Error while trying to checkout %s from repo %s" % (self.id, self.repository.url))
                try:
                    os.remove(self.path + "/.gitignore")
                except OSError:
                    pass
                shutil.rmtree(self.path + "/.git")

    def get_library(self):
        self.fetch()
        return Library(self.id, self.path, self.mc)

    def run(self, args):
        return subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=self.path)

