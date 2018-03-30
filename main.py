from flask import Flask
from app.routes.index import index_routes
from app.routes.repo import repo_routes
from app.flask_shared import app

app.register_blueprint(index_routes)
app.register_blueprint(repo_routes)

if __name__ == "__main__":
    app.run()
