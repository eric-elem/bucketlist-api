""" APIs main module """

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

APP = Flask(__name__)
DB = SQLAlchemy(APP)

if __name__ == '__main__':
    APP.run(debug=True)
