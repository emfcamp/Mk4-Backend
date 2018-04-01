from app.util import memcached
from os.path import *

class Sizer:
    def __init__(self, mc=memcached.shared):
        self.mc = mc

    def get_size(self, path):
        key = "get_size::" + path
        cached_result = self.mc.get(key)
        if cached_result:
            return cached_result

        result = getsize(path)

        self.mc.set(key, result)
        return result

