from flask import Flask, jsonify, Blueprint
from ..flask_shared import app
from ..util.memcached import shared
import shutil
from os.path import *
import tempfile

index_routes = Blueprint('index_routes', __name__)

@index_routes.route("/")
def hello_world():
    app.logger.info("Hello world")
    return jsonify({"hello": "world"})

@index_routes.route("/poke", methods=['POST'])
def poke():
    app.logger.info("Flush")
    shared.flush_all()
    app.logger.info("Remove")
    shutil.rmtree(normpath(tempfile.gettempdir() + "/badgestore-cache/"))
    app.logger.info("Done")
    return jsonify({"poked": True})
