from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import configuration
from app.blueprints.auth.views import auth
from app.blueprints.bucketlists.views import bucketlists

def create_app(configuration_name):
    app = Flask(__name__)
    app.config.from_object(configuration[configuration_name])
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(bucketlists, url_prefix='/bucketlists')
    db = SQLAlchemy(app)
    migrate = Migrate(app, db)

    return app