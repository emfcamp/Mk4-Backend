from flask import Flask, jsonify, Blueprint, request
from ..models.repository import Repository
from ..flask_shared import app

repo_routes = Blueprint('repo_routes', __name__)

@repo_routes.route("/refs")
def repo_home():
    repository = Repository(repo())
    refs = repository.list_references()
    return jsonify({'refs': refs})

@repo_routes.route("/library")
def repo_reference():
    library = get_library(repo(), ref())
    if library.errors:
        return handle_ref_error(library)

    return jsonify({'commit_id': library.commit_id, 'dependencies': library.dependencies, 'apps': library.apps})

@repo_routes.route("/check")
def repo_check():
    library = get_library(repo(), ref())
    if library.errors:
        return handle_ref_error(library)

    return jsonify({'pass': True, 'commit_id': library.commit_id, 'ref': ref()})

@repo_routes.route("/apps")
def repo_categories():
    library = get_library(repo(), ref())
    if library.errors:
        return handle_ref_error(library)

    return jsonify(library.get_apps_by_category())

@repo_routes.route("/app")
def repo_app():
    library = get_library(repo(), ref())
    if library.errors:
        return handle_ref_error(library)

    app = required_param('app')

    if app not in library.apps:
        return jsonify({'error': 'app not found in library'}), 404

    return jsonify(library.apps[app])

@repo_routes.route("/install")
def repo_install():
    library = get_library(repo(), ref())
    if library.errors:
        return handle_ref_error(library)

    files = {}
    for app_name in required_param('apps').split(","):
        if app_name not in library.apps:
            return jsonify({'error': 'app %s not found in library' % app_name}), 404

        app = library.apps[app_name]
        files[app_name] = {}
        for file, hashcode in app['files'].items():
            files[app_name][file] = hashcode

    return jsonify(files)

def repo():
    return required_param("repo")

def ref():
    return request.args.get("ref", default="master")

def required_param(name):
    print(name)
    result = request.args.get(name)
    if not result:
        raise Exception("Query parameter '%s' is required" % name)
    return result

def get_library(repo, ref):
    library = Repository(repo).get_commit(ref).get_library()
    library.scan()
    return library;

def handle_ref_error(library):
    return jsonify({'commit_id': library.commit_id, 'errors': library.get_compact_errors(), 'ref': ref()}), 400
