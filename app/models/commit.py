import subprocess, shutil, os
from .cache_folder import CacheFolder
from ..flask_shared import app
from .store_snapshot import StoreSnapshot

class Commit:
    def __init__(self, repository, id, mc):
        self.repository = repository
        self.id = id
        self.cache_folder = CacheFolder()
        self.mc = mc

    # useful for testing
    def clean(self):
        shutil.rmtree(self.get_folder(), ignore_errors=True)

    def ensure_existence(self, retry=3):
        if not os.path.isdir(self.get_folder()):
            try:
                app.logger.info("Checking out %s from repository %s" % (self.id, self.repository.url))
                shutil.copytree(self.repository.get_cached_folder(), self.get_folder(), ignore=shutil.ignore_patterns('.*'))
            except Exception as err:
                if retry == 0:
                    raise err
                # Possible race condition scenario, let's retry
                self.update(retry - 1)

    def get_all_hashes(self):
        key = "commit_all_hashes::" + self.id
        cached_result = self.mc.get(key)
        if cached_result:
            return cached_result

        self.ensure_existence()
        cwd = self.get_folder()
        print(cwd)
        # This is somewhat un-portable, but it should work for now
        response = subprocess.run("find . -type f | xargs shasum", stdout=subprocess.PIPE, cwd=cwd, shell=True)
        if response.returncode != 0:
            raise Exception("Error retrieving hashes")

        result = {}
        for line in response.stdout.decode('utf-8').splitlines():
            [hash, filename] = line.split(None, 1)
            result[filename[2:]] = hash

        self.mc.set(key, result)
        return result

    def get_store_snapshot():
        return StoreSnapshot(self, self.mc)

    def get_folder(self):
        return self.cache_folder.get_path("ref_" + self.id)

