import subprocess
from app.util import memcached
from ..util.cache_folder import CacheFolder
from .commit import Commit
from ..flask_shared import app
import re, hashlib, shutil

class Repository:
    def __init__(self, url, mc=memcached.shared):
        # if it doesn't look like a full git url, assume it's github
        if (not url.startswith("file:")) and (not url.startswith("http:")) and (not url.startswith("https:")) and (not url.startswith("ssh:")):
            url = "https://github.com/%s.git" % url
        self.url = url
        self.mc = mc
        self.path = CacheFolder().get("rep_" + hashlib.sha224(self.url.encode('utf-8')).hexdigest()[:10] + "_" + re.sub(r'\W+', '_', self.url)[:40])

    def update(self, retry=True):
        key = "repository_update::" + self.url
        if self.mc.get(key):
            # skipping update since we've already done so recently
            return
        app.logger.info("Updating repo %s" % self.url)
        self.mc.set(key, "updated", time=60)

        result = self.run(['git', 'status'])
        if result.returncode == 0:
            # We already have a repo
            result = self.run(['git', 'fetch', '--all'])
            if result.returncode == 0:
                # for branches already checked out, most likely only master
                result = self.run(['git', 'pull', '--all'])
            if result.returncode != 0:
                app.logger.info("There was a problem updating an existing repo: %s" % result)
                if retry:
                    # Something went wrong. Nuke the repo and try again
                    app.logger.info("Clearing folder %s and trying again" % self.path)
                    shutil.rmtree(self.path)
                    self.update(False)
                else:
                    app.logger.error("We've already retried, giving up")
                    raise Exception("Repository %s is unavailable or invalid" % self.url)
        else:
            app.logger.info("Checking out new repo to %s" % self.path)
            result = self.run(['git', 'clone', self.url, '.'])

        if result.returncode != 0:
            app.logger.warn(result)
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
        app.logger.warn("Reference %s not found, path %s" % (rev, self.path))
        raise Exception("Reference %s not found, please try again later if you're sure it exists" % rev)

    def run(self, args):
        return subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=self.path)




