import subprocess, shutil, os
from ..util.cache_folder import CacheFolder
from ..flask_shared import app
from .library import Library

class Commit:
    def __init__(self, repository, id, mc):
        self.repository = repository
        self.id = id
        self.mc = mc
        self.path = CacheFolder().get_path("ref_" + self.id)

    def clean_up(self):
        shutil.rmtree(self.path, ignore_errors=True)

    def fetch(self, retry=3):
        if not os.path.isdir(self.path):
            try:
                app.logger.info("Checking out %s from repository %s" % (self.id, self.repository.url))
                shutil.copytree(self.repository.path, self.path, ignore=shutil.ignore_patterns('.*'))
            except Exception as err:
                if retry == 0:
                    raise err
                # Possible race condition scenario, let's retry
                self.ensure_existence(retry - 1)

    def get_library(self):
        self.fetch()
        return Library(self.id, self.path, self.mc)

