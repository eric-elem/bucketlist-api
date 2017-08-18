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

class Bucketlist(DB.Model):
    """ Models the bucketlist table """

    __tablename__ = 'bucketlists'
    identity = DB.Column(DB.Integer, primary_key=True)
    title = DB.Column(DB.String(256), unique=True)
    user_id = DB.Column(DB.Integer, DB.ForeignKey('users.id'))
    items = DB.relationship('Item', backref=DB.backref('bucketlist', lazy='dynamic'),
                            lazy='dynamic')

    def __init__(self, title, user):
        self.title = title
        self.user = user

    def update_bucketlist(self, title):
        """ Changes the title of a bucket to the provided title """
        self.title = title
    
class Item(DB.Model):
    """ Models the items table """

    __tablename__ = items
    identity = DB.Column(DB.Integer, primary_key=True)
    description = DB.Column(DB.String(256), unique=True)
    status = DB.Column(DB.Boolean)
    bucketlist_id = DB.Column(DB.Integer, DB.ForeignKey('bucketlists.id'))

    def __init__(self, description, bucketlist):
        self.description = description
        self.status = False
        self.bucketlist = bucketlist

    def update_item(self, description, status):
        """ Modifies item """
        self.description = description
        self.status = status
