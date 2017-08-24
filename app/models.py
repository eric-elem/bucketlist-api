""" Defines data models """
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class User(db.Model):
    """ Models the users table """

    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))
    password = db.Column(db.String(256))
    name = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(),
                           onupdate=db.func.current_timestamp())
    bucketlists = db.relationship('Bucketlist', backref='user', lazy='dynamic')
    logged_out_tokens = db.relationship('LoggedoutToken', backref='user',
                                        lazy='dynamic')

    def __init__(self, username, password, name):
        self.username = username
        self.set_password(password)
        self.name = name

    def set_password(self, password):
        """ Hashes and sets the provided password for a user """
        self.password = generate_password_hash(password)

    def verify_password(self, password):
        """ Hashes and checks if the provided password matches that
        stored for the user """
        return check_password_hash(self.password, password)


class Bucketlist(db.Model):
    """ Models the bucketlist table """

    __tablename__ = 'bucketlists'
    bucketlist_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), unique=True)
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    items = db.relationship('Item', backref='bucketlist', lazy='dynamic')
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(),
                           onupdate=db.func.current_timestamp())

    def __init__(self, title, description, user_id):
        self.title = title
        self.description = description
        self.user_id = user_id


class Item(db.Model):
    """ Models the items table """

    __tablename__ = 'items'
    item_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), unique=True)
    description = db.Column(db.Text)
    status = db.Column(db.Boolean)
    bucketlist_id = db.Column(db.Integer, db.ForeignKey(
                                                'bucketlists.bucketlist_id'))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(),
                           onupdate=db.func.current_timestamp())

    def __init__(self, title, description, bucketlist_id):
        self.title = title
        self.description = description
        self.status = False
        self.bucketlist_id = bucketlist_id


class LoggedoutToken(db.Model):
    """ Models a logged out token """

    __tablename__ = 'loggedouttokens'
    token_id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(256))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))

    def __init__(self, token, user_id):
        self.token = token
        self.user_id = user_id
