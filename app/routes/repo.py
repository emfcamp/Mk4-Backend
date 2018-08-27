from flask import Flask, jsonify, Blueprint, request, send_from_directory
from ..models.repository import Repository
from ..models.github import Github
from ..flask_shared import app
from ..models.invalid_usage import InvalidUsage

repo_routes = Blueprint('repo_routes', __name__)

@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

@repo_routes.route("/refs")
def repo_home():
    repository = Repository(repo())
    refs = repository.list_references()
    return jsonify({'refs': refs})

@repo_routes.route("/prs")
def repo_prs():
    github = Github(repo())
    return jsonify(github.get_prs())

@repo_routes.route("/library")
def repo_reference():
    library = get_library(repo(), ref())
    if library.has_errors():
        return handle_error(library)

    return jsonify({'commit_id': library.commit_id, 'resources': library.resources})

@repo_routes.route("/check")
def repo_check():
    library = get_library(repo(), ref())
    if library.has_errors():
        return handle_error(library)

    return "ref: %s\ncommit_id: %s\n\nPASS 🚢" % (ref(), library.commit_id), 200, {'Content-Type': 'text/plain; charset=utf-8'}
@repo_routes.route("/apps")
def repo_categories():
    library = get_library(repo(), ref())
    if library.has_errors():
        return handle_error(library)

    return jsonify(library.categories)

@repo_routes.route("/app")
def repo_app():
    library = get_library(repo(), ref())
    if library.has_errors():
        return handle_error(library)

    app = required_param('app')

    if app not in library.resources:
        return jsonify({'error': 'app not found in library'}), 404

    return jsonify(library.resources[app])

@repo_routes.route("/download")
def repo_download():
    library = get_library(repo(), ref())
    if library.has_errors():
        return handle_error(library)

    return send_from_directory(library.path, required_param("path"))

@repo_routes.route("/install")
def repo_install():
    library = get_library(repo(), ref())
    if library.has_errors():
        return handle_error(library)

    return get_files(library, required_param('apps').split(","))

@repo_routes.route("/bootstrap")
def repo_bootstrap():
    library = get_library("emfcamp/Mk4-Apps", ref())
    if library.has_errors():
        return handle_error(library)

    apps = [name for (name, r) in library.resources.items() if (r['type'] == "app") and r.get("bootstrapped", False)]
    return get_files(library, apps)

@repo_routes.route("/flash")
def repo_flash():
    library = get_library(repo(), ref())
    if library.has_errors():
        return handle_error(library)

    return get_files(library, ["bootstrap"])

def get_files(library, apps):
    files = {}
    for app_name in apps + ["boot.py"]:
        if app_name not in library.resources:
            return jsonify({'error': 'app %s not found in library' % app_name}), 404

        app = library.resources[app_name]
        for file, hashcode in app['files'].items():
            files[file] = hashcode

    return jsonify(files)

def repo():
    return required_param("repo")

def ref():
    return request.args.get("ref", default="master")

def required_param(name):
    result = request.args.get(name)
    if not result:
        raise InvalidUsage("Query parameter '%s' is required" % name)
    return result

def get_library(repo, ref):
    library = Repository(repo).get_commit(ref).get_library()
    return library;

def handle_error(library):
    return "ref: %s\ncommit_id: %s\n\n%s" % (ref(), library.commit_id, library.get_error_summary()), 400, {'Content-Type': 'text/plain; charset=utf-8'}
