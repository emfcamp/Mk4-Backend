import subprocess, os
from os.path import *

class CacheFolder:
    def __init__(self, path = normpath(dirname(__file__) + "../../../cache/")):
        self.path = path

    def get(self, name):
        path = normpath(self.path + "/" + name)
        if not os.path.isdir(path):
            os.makedirs(path)
        return path


