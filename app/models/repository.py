import subprocess
from app.util import memcached
from .cache_folder import CacheFolder
from .commit import Commit
from ..flask_shared import app
import re, hashlib

class Repository:
    def __init__(self, url, mc=memcached.shared):
        self.url = url
        self.mc = mc
        self.cache_folder = CacheFolder()

    def update(self):
        key = "repository_update::" + self.url
        if self.mc.get(key):
            # skipping update since we've already done so recently
            return
        app.logger.info("Updating repo %s" % self.url)
        self.mc.set(key, "updated", time=60)

        result = self.run(['git', 'status'])
        if result.returncode == 0:
            result = self.run(['git', 'fetch', '--all'])
        else:
            app.logger.info("Checking out new repo to %s" % self.get_cached_folder())
            result = self.run(['git', 'clone', self.url, '.'])

        if result.returncode != 0:
            raise Exception("Repository %s is unavailable or invalid" % self.url)

    def list_references(self):
        self.update();
        data = self.run(['git', 'branch', '-r']).stdout.decode('utf-8')
        lines = data.splitlines()
        return [l[9:] for l in lines if "HEAD" not in l]

    def get_commit(self, rev):
        self.update()
        result = self.run(["git", "rev-parse", rev])
        if result.returncode != 0:
            # in case of non-master branches or tags
            result = self.run(["git", "rev-parse", "origin/" + rev])
        if result.returncode == 0:
            return Commit(self, result.stdout.decode('utf-8').strip(), mc=self.mc)
        app.logger.warn("Reference %s not found, path %s" % (rev, self.get_path_name()))
        raise Exception("Reference %s not found, please try again later if you're sure it exists" % rev)

    # generates a unique but somewhat human-readable string that is safe to use in filesystems
    def get_path_name(self):
        hash = hashlib.sha224(self.url.encode('utf-8')).hexdigest()[:10]
        return "rep_" + hash + "_" + re.sub(r'\W+', '_', self.url)[:40]

    # todo: memoization
    def get_cached_folder(self):
        return self.cache_folder.get(self.get_path_name())

    # helper method that executes a command in the local folder
    def run(self, args):
        cwd = self.get_cached_folder()
        response = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)
        return response




