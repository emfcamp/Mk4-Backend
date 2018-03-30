from flask import Flask, jsonify, Blueprint
from ..models.repository import Repository
from ..flask_shared import app

repo_routes = Blueprint('repo_routes', __name__)

@repo_routes.route("/repo/<path:repo>/")
def repo_home(repo):
    repository = Repository(repo)
    refs = repository.list_references()
    return jsonify({'refs': list(refs.keys())})

@repo_routes.route("/repo/<path:repo>/ref/<ref>")
def repo_reference(repo, ref):
    repository = Repository(repo)

    refs = repository.list_references()
    return jsonify({'refs': list(refs.keys())})

