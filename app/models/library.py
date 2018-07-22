import subprocess, shutil, os, re
from ..util.cache_folder import CacheFolder
from ..flask_shared import app
from ..util.resources import *

# Abstraction on top of a particular commit
class Library:
    def __init__(self, commit_id, path, mc):
        self.commit_id = commit_id
        self.path = path
        self.mc = mc

    @property
    def resources(self):
        key = "library_parse::v2::" + self.commit_id
        resources = self.mc.get(key)
        if resources:
            return resources

        resources = get_resources(self.path)
        add_hashes(self.path, resources)
        add_metadata(self.path, resources)
        resolve_dependencies(resources)
        validate(self.path, resources)

        self.mc.set(key, resources)
        return resources

    @property
    def categories(self):
        categories = {}
        for app_name, app in self.resources.items():
            if app['type'] != "app":
                continue
            if 'categories' in app:
                for category in app['categories']:
                    categories.setdefault(category, []).append(app_name)
        for apps in categories.values():
            apps.sort()
        return categories

    def get_error_summary(self):
        return get_error_summary(self.resources)

    def has_errors(self):
        for key, resource in self.resources.items():
            if "errors" in resource:
                return True
        return False
