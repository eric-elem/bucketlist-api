from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import configuration

db = SQLAlchemy()
app = Flask(__name__)


@app.errorhandler(404)
def handle_errors(e):
    response = {
        'status': 'Error',
        'message': 'The URL you in your request does not exist'
    }
    return jsonify(response), 404


def create_app(configuration_name):
    app.config.from_object(configuration[configuration_name])
    db.init_app(app)

    from app.api.auth.views import auth
    from app.api.bucketlists.views import bucketlists
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(bucketlists, url_prefix='/bucketlists')

    migrate = Migrate(app, db)

    return app
