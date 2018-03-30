from flask import Flask, jsonify, Blueprint
from ..flask_shared import app

index_routes = Blueprint('index_routes', __name__)

@index_routes.route("/")
def hello_world():
    app.logger.info("Hello world")
    return jsonify({"hello": "world"})
