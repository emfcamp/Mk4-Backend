import subprocess, shutil, os, re
from ..util.cache_folder import CacheFolder
from ..util.hasher import Hasher
from ..util.sizer import Sizer
from ..util.metadata_parser import MetadataParser
from ..util.validation_error import ValidationError
from ..flask_shared import app

lib_path_pattern = re.compile(r"^libs/([a-zA-Z0-9_\-]{2,20})\.py$")
app_path_pattern = re.compile(r"([a-zA-Z0-9_\-]{2,20})/([a-zA-Z0-9_\/\-\.]{2,40})$")
lib_metadata_rules = {
    'description': {'type': 'string', 'required': True, 'min': 5, 'max': 200},
    'dependencies': {'type': 'list', 'default': [], 'max': 10},
    'license': {'type': 'string', 'required': True, 'min':1, 'max': 140}
}
app_metadata_rules = {
    'description': {'type': 'string', 'required': True, 'min': 5, 'max': 200},
    'categories': {'type': 'list', 'min': 1, 'max': 3},
    'dependencies': {'type': 'list', 'default': [], 'max': 10},
    'built-in': {'type': 'boolean', 'default': False},
    'license': {'type': 'string', 'required': True, 'min':1, 'max': 140}
}
max_app_size_before_dependencies = 30000 # we should really get this down

# Abstraction on top of a particular commit, acts like a parser on top of a folder
# Main functionality is dependency resolution and validation
class Library:
    def __init__(self, commit_id, path, mc, hasher=Hasher(), metadata_parser=MetadataParser(), sizer=Sizer()):
        self.commit_id = commit_id
        self.path = path
        self.mc = mc
        self.hasher = hasher
        self.metadata_parser = metadata_parser
        self.sizer = sizer

    # Todo: This function could do with a refactor.
    def scan(self):
        key = "library_parse::" + self.commit_id
        cached_result = self.mc.get(key)
        if cached_result:
            [self.apps, self.libs, self.errors] = cached_result;
            return

        hashes = self.hasher.get_hashes(self.path)
        hashes = {k: v for k, v in hashes.items() if "/" in k}

        libs = {}
        apps = {}
        errors = []

        for path, hash in hashes.items():
            full_path = "%s/%s" % (self.path, path)
            size = self.sizer.get_size(full_path)
            if path.startswith("libs/"):
                # validate filename
                matches = lib_path_pattern.match(path)
                if not matches:
                    errors.append(ValidationError(path, "Library file validation failed: %s is not a valid library file name" % path))
                    continue

                result = self.metadata_parser.parse(full_path, path, lib_metadata_rules)
                if isinstance(result, list):
                    errors.extend(result)
                    continue

                libs[matches.group(1)] = result
                libs[matches.group(1)]['hash'] = hash
                libs[matches.group(1)]['size'] = size
            else:
                matches = app_path_pattern.match(path)
                if not matches:
                    errors.append(ValidationError(path, "Invalid path"))
                    continue

                app_name = matches.group(1)
                file_name = matches.group(2)

                if app_name not in apps:
                    apps[app_name] = {'files': {}, 'size': 0}

                if file_name == 'main.py':
                    result = self.metadata_parser.parse(full_path, path, app_metadata_rules)
                    if isinstance(result, list):
                        errors.extend(result)
                        continue
                    apps[app_name].update(result)

                apps[app_name]['files'][path] = hash
                apps[app_name]['size'] += size

        # validate lib dependencies
        for lib, info in libs.items():
            dependencies_not_found = [d for d in info['dependencies'] if d not in libs]
            if dependencies_not_found:
                errors.append(ValidationError('libs/%s.py' % lib, "Dependencies not found: %s" % dependencies_not_found))
                continue


            # resolve dependencies
            info['files'] = {}
            to_be_added = set([lib])
            resolved_dependencies = set()
            while len(to_be_added) > 0:
                l = to_be_added.pop()
                path = "libs/%s.py" % l
                info['files'][path] = hashes[path]
                resolved_dependencies.add(l)
                for required_lib in libs[l]['dependencies']:
                    if required_lib not in resolved_dependencies:
                        to_be_added.add(required_lib)

        # resolve app dependencies and check size
        for app, info in apps.items():
            main_file = '%s/main.py' % app
            if main_file not in hashes:
                errors.append(ValidationError(main_file, 'main.py file not provided'))
                continue

            if info['size'] > max_app_size_before_dependencies:
                errors.append(ValidationError(main_file, "App %s is a total of %d bytes, allowed maximum is %d" % (app, info['size'], max_app_size_before_dependencies)))
                continue

            if 'dependencies' in info:
                for dependency in info['dependencies']:
                    if dependency not in libs:
                        errors.append(ValidationError(main_file, "Dependency not found: %s" % dependency))
                        continue

                    for dependency in info['dependencies']:
                        info['files'].update(libs[dependency]['files'])

        if errors:
            self.mc.set(key, [None, None, errors])
            # do this at the end to avoid problems in case of a race condition
            self.libs = None
            self.apps = None
            self.errors = errors
        else:
            self.mc.set(key, [apps, libs, None])
            self.libs = libs
            self.apps = apps
            self.errors = None

    def get_compact_errors(self):
        errors = {}
        for error in self.errors:
            if error.name not in errors:
                errors[error.name] = []
            errors[error.name].append(error.message)
        return errors

    def get_apps_by_category(self):
        categories = {}
        for app_name, app in self.apps.items():
            if 'categories' in app:
                for category in app['categories']:
                    if category not in categories:
                        categories[category] = []
                    categories[category].append(app_name)
        return categories
