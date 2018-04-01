from flask import Flask, jsonify, Blueprint
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
    library = Repository(repo).get_commit(ref).get_library()
    library.scan()
    if library.errors:
        errors = [str(e) for e in library.errors]
        return jsonify({'commit_id': library.commit_id, 'errors': errors}), 400
    else:
        return jsonify({'commit_id': library.commit_id, 'libs': library.libs, 'apps': library.apps})

