""" Defines data models """
from app import DB
from werkzeug.security import generate_password_hash, check_password_hash

class User(DB.Model):
    """ Models the users table """

    __tablename__ = 'users'
    identity = DB.Column(DB.Integer, primary_key=True)
    username = DB.Column(DB.String(20), unique=True)
    password = DB.Column(DB.String(256))
    name = DB.Column(DB.String(50))
    bucketlists = DB.relationship('Bucketlist', backref=DB.backref('user', lazy='dynamic'),
                                  lazy='dynamic')

    def __init__(self, username, password, name):
        self.username = username
        self.set_password(password)
        self.name = name

    def set_password(self, password):
        """ Hashes and sets the provided password for a user """
        self.password = generate_password_hash(password)

    def verify_password(self, password):
        """ Hashes and checks if the provided password matches that stored for the user """
        return check_password_hash(self.password, password)
