import subprocess
from app.util import memcached
from .cache_folder import CacheFolder
from ..flask_shared import app
import re, hashlib

class Repository:
    def __init__(self, url, mc=memcached.shared):
        self.url = url
        self.mc = mc
        self.cache_folder = CacheFolder()

    def list_references(self):
        key = "repository_list_refererences::" + self.url
        result = self.mc.get(key)
        if result:
            return result

        app.logger.info("fetching references for %s from git" % self.url)
        data = subprocess.run(['git', 'ls-remote', '-h', self.url], stdout=subprocess.PIPE).stdout.decode('utf-8')
        lines = data.splitlines()
        result = {}
        for line in lines:
            [commit_id, ref] = line.split()
            result[ref[11:]] = commit_id

        self.mc.set(key, result, time=60)

        return result

    # generates a unique but somewhat human-readable string that is safe to use in filesystems
    def get_path_name(self):
        print(self.url)
        hash = hashlib.sha224(self.url.encode('utf-8')).hexdigest()[:10]
        return hash + "_" + re.sub(r'\W+', '_', self.url)[:69]

    def fetch(self):
        self.cache_folder.get()
        subprocess.run(['git', 'ls-remote', '-h', self.url], stdout=subprocess.PIPE)


