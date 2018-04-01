import subprocess, os
from os.path import *
import tempfile

class CacheFolder:
    def __init__(self, path = normpath(tempfile.gettempdir() + "/badgestore-cache/")):
        self.path = path

    def get_path(self, name):
        return normpath(self.path + "/" + name)

    def exists(self, name):
        return os.path.isdir(self.get_path(name))

    def get(self, name):
        path = self.get_path(name)
        if not os.path.isdir(path):
            os.makedirs(path)
        return path


