import subprocess, os
from app.util import memcached
from ..util.cache_folder import CacheFolder
from .commit import Commit
from ..flask_shared import app
import re, hashlib, shutil
from ..util.lock_pool import shared_lock

class Repository:
    def __init__(self, url, mc=memcached.shared):
        # if it doesn't look like a full git url, assume it's github
        if (not url.startswith("file:")) and (not url.startswith("http:")) and (not url.startswith("https:")) and (not url.startswith("ssh:")):
            url = "https://github.com/%s.git" % url
        self.url = url
        self.mc = mc
        self.path = CacheFolder().get("rep_" + hashlib.sha224(self.url.encode('utf-8')).hexdigest()[:10] + "_" + re.sub(r'\W+', '_', self.url)[:40])

    def update(self, force=False, retry=True):
        key = "repository_update::" + self.url

        # Use a lock to avoid multiple requests entering this block at the same time. I have no
        # idea how well this will actually work.
        result = None
        with shared_lock(key):
            if not force:
                cached = self.mc.get(key)
                if cached:
                    # skipping update since we've already done so recently
                    if cached == "invalid":
                        raise Exception("Repository %s is unavailable or invalid" % self.url)
                    return


            if not os.path.isdir(self.path):
                app.logger.warn("For some reason the directory doesn't exists - create it")
                os.makedirs(self.path, exist_ok=True)

            app.logger.info("Updating repo %s" % self.url)
            result = self.run(['git', '-c', 'core.askpass=true', 'status'])
            if result.returncode > 0:
                app.logger.info("Checking out new repo to %s" % self.path)
                result = self.run(['git', '-c', 'core.askpass=true', 'clone', self.url, '.'])
                if result.returncode > 0:
                    # No point retrying a failed clone
                    retry = False

            if result.returncode == 0:
                result = self.run_many([
                    ['git', '-c', 'core.askpass=true', 'fetch', '--all'],
                    ['git', '-c', 'core.askpass=true', 'fetch', '--tags', '--progress', 'origin', 'refs/pull/*:refs/remotes/origin/pr/*'],
                    ['git', '-c', 'core.askpass=true', 'pull', '--all']
                ])

        if result.returncode > 0:
            app.logger.info("There was a problem updating an existing repo: %s" % result)
            if retry:
                # Something went wrong. Nuke the repo and try again
                app.logger.info("Clearing folder %s and trying again" % self.path)
                shutil.rmtree(self.path)
                self.update(retry=False)
            else:
                app.logger.error("We've already retried, giving up")
                self.mc.set(key, "invalid", time=60)
                raise Exception("Repository %s is unavailable or invalid" % self.url)

            if result.returncode == 0:
                self.mc.set(key, "updated", time=60)
            else:
                app.logger.warn(result)
                self.mc.set(key, "invalid", time=60)
                raise Exception("Repository %s is unavailable or invalid" % self.url)

    def list_references(self):
        self.update();
        data = self.run(['git', 'branch', '-r']).stdout.decode('utf-8')
        lines = data.splitlines()
        return [l[9:] for l in lines if "HEAD" not in l]

    def get_commit(self, rev):
        self.update()

        #result = self.run(["git", 'cat-file', "-t", rev])
        #if result.returncode > 0:
        #    app.logger.info("commit not found, trying to fetch in case its a remote branch")
        #    result = self.run(["git", "-c", 'core.askpass=true',"fetch",  "origin", rev])
        #    if result.returncode == 0:
        #        return Commit(self, result.stdout.decode('utf-8').strip(), mc=self.mc)

        result = self.run(["git", "rev-parse", rev])
        if result.returncode > 0:
            result = self.run(["git", "rev-parse", "origin/" + rev])
        if result.returncode == 0:
            return Commit(self, result.stdout.decode('utf-8').strip(), mc=self.mc)

        app.logger.warn("Reference %s not found, path %s" % (rev, self.path))
        raise Exception("Reference %s not found, please try again later if you're sure it exists" % rev)

    def run_many(self, argss):
        result = None
        for args in argss:
            result = self.run(args)
            if result.returncode > 0:
                break
        return result



    def run(self, args):
        result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=self.path)
        app.logger.debug(result)
        return result




