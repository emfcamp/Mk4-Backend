from flask import Flask, jsonify, Blueprint, request
from ..models.repository import Repository
from ..flask_shared import app

repo_routes = Blueprint('repo_routes', __name__)

@repo_routes.route("/repo/<path:repo>/")
def repo_home(repo):
    repository = Repository(repo)
    refs = repository.list_references()
    return jsonify({'refs': refs})

@repo_routes.route("/repo/<path:repo>/ref/<ref>")
def repo_reference(repo, ref):
    library = get_library(repo, ref)
    if library.errors:
        return handle_ref_error(library)

    return jsonify({'commit_id': library.commit_id, 'libs': library.libs, 'apps': library.apps})

@repo_routes.route("/repo/<path:repo>/ref/<ref>/categories/")
def repo_categories(repo, ref):
    library = get_library(repo, ref)
    if library.errors:
        return handle_ref_error(library)

    return jsonify(library.get_apps_by_category())

@repo_routes.route("/repo/<path:repo>/ref/<ref>/app/<app>/")
def repo_app(repo, ref, app):
    library = get_library(repo, ref)
    if library.errors:
        return handle_ref_error(library)

    if app not in library.apps:
        return jsonify({'error': 'app not found in library'}), 404

    return jsonify(library.apps[app])

@repo_routes.route("/repo/<path:repo>/ref/<ref>/install/<apps>/")
def repo_install(repo, ref, apps):
    library = get_library(repo, ref)
    if library.errors:
        return handle_ref_error(library)

    files = {}
    for app_name in apps.split(","):
        if app_name not in library.apps:
            return jsonify({'error': 'app %s not found in library' % app_name}), 404

        app = library.apps[app_name]
        files[app_name] = {}
        for file, hashcode in app['files'].items():
            files[app_name][file] = hashcode

    return jsonify(files)

def get_library(repo, ref):
    library = Repository(repo).get_commit(ref).get_library()
    library.scan()
    return library;

def handle_ref_error(library):
    return jsonify({'commit_id': library.commit_id, 'errors': library.get_compact_errors()}), 400
