from app.util import memcached
import subprocess

class Hasher:
    def __init__(self, mc=memcached.shared):
        self.mc = mc

    def get_hashes(self, path):
        key = "get_hashes::" + path
        cached_result = self.mc.get(key)
        if cached_result:
            return cached_result

        # This is somewhat un-portable, but it should work for now
        response = subprocess.run("find . -type f -not -path '*/\.*' | xargs shasum", stdout=subprocess.PIPE, cwd=path, shell=True)
        if response.returncode != 0:
            raise Exception("Error retrieving hashes")

        result = {}
        for line in response.stdout.decode('utf-8').splitlines():
            [hash, filename] = line.split(None, 1)
            result[filename[2:]] = hash

        self.mc.set(key, result)
        return result

