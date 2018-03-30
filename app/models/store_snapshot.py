import subprocess, shutil, os
from .cache_folder import CacheFolder
from ..flask_shared import app

# Abstraction on top of a particular commit, provides high-level functionality
class StoreSnapshot:
    def __init__(self, commit, mc):
        self.commit = commit
        self.mc = mc

    # creates map of apps
    def parse_folder():
        self.apps = {}


