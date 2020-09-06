from flask import Flask
from flask_core import app as flask_app

if __name__ == "__main__":
    app = Flask(__name__)
    app.register_blueprint(flask_app)
    app.run()