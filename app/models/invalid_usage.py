from flask import jsonify, request
from ..flask_shared import app

class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload
        try:
            app.logger.warn("Invalid usage exception: %s (%s)" % (message, request.url))
        except:
            pass

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

    def __str__(self):
        return self.message
