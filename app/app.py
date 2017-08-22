""" APIs main module """
from flask import Flask

APP = Flask(__name__)
APP.config['SECRET_KEY'] = '254HHSY18836'
APP.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

from views import *

if __name__ == '__main__':
    APP.run(debug=True)
