""" Applications view methods """

from functools import wraps
import datetime
import jwt
from flask import Blueprint, request, jsonify
from models import DB, APP, User, Bucketlist, Item, LoggedoutToken

auth = Blueprint('auth', __name__)

def token_required(func):
    """ Defines a decorator for views requiring token authentication """
    @wraps(func)
    def decorated(*args, **kwargs):
        """ Defines the decorated function """
        if 'x-access-token' in request.headers:
            received_token = request.headers['x-access-token']
            if LoggedoutToken.query.filter_by(token=received_token).first():
                return generate_response('Login for a new token'), 401
            else:
                try:
                    token_data = jwt.decode(received_token, APP.config['SECRET_KEY'])
                    the_user = User.query.filter_by(username=token_data['username']).first()
                    if the_user:
                        return func(the_user, *args, **kwargs)
                    return generate_response('User not found'), 404
                except jwt.ExpiredSignatureError:
                    return generate_response('Token expired'), 498
                except jwt.InvalidTokenError:
                    return generate_response('Invalid token'), 498
        return generate_response('Token required'), 401
    return decorated

@AUTH.route('/register', methods=['POST'])
def register():
    """ Handles signing up new users """
    #silent attribute ensures None is returned and no exception is thrown if get_json fails
    new_user = request.get_json(silent=True)
    if new_user:
        if 'name' in new_user and 'username' in new_user and 'password' in new_user\
            and 'password_rpt' in new_user:
            if new_user['password'] == new_user['password_rpt']:
                user = get_user(new_user['username'])
                if not user:
                    user = User(new_user['username'], new_user['password'], new_user['name'])
                    DB.session.add(user)
                    DB.session.commit()
                    return generate_response('User added'), 201
                return generate_response('User already exists'), 202
            return generate_response('Passwords do not match'), 400
        return generate_response('Invalid keys'), 400
    return generate_response('Provide JSON data'), 400

@AUTH.route('/login', methods=['POST'])
def login():
    """ Handles signing in users """
    credentials = request.get_json(silent=True)
    if credentials:
        if 'username' in credentials and 'password' in credentials:
            user = get_user(credentials['username'])
            if user:
                if user.verify_password(credentials['password']):
                    DB.session.query(LoggedoutToken).filter_by(user_id=user.identity).delete()
                    DB.session.commit()
                    token = jwt.encode({'username' : credentials['username'],
                                        'exp' : datetime.datetime.utcnow() +
                                                datetime.timedelta(minutes=15)},
                                       APP.config['SECRET_KEY'])
                    return jsonify({'token' : token.decode('UTF-8')}), 200
                return generate_response('Invalid password'), 401
            return generate_response('User not found'), 404
        return generate_response('Invalid keys'), 400
    return generate_response('Provide JSON data'), 400

@AUTH.route('/logout')
@token_required
def logout(the_user):
    """ Handles user logout """
    users_token = request.headers['x-access-token']
    logged_out_token = LoggedoutToken(users_token, the_user.identity)
    DB.session.add(logged_out_token)
    DB.session.commit()
    return generate_response('You have been logged out'), 200

@AUTH.route('/reset-password', methods=['POST'])
@token_required
def reset_password(the_user):
    """ Updates users password """
    new_user_details = request.get_json(silent=True)
    if new_user_details:
        if ('password' in new_user_details
                and 'new_password' in new_user_details and
                'new_password_rpt' in new_user_details):
            if the_user.verify_password(new_user_details['password']):
                if new_user_details['new_password'] == new_user_details['new_password_rpt']:
                    the_user.set_password(new_user_details['new_password'])
                    DB.session.add(the_user)
                    DB.session.commit()
                    return generate_response('Password updated'), 200
                return generate_response('New passwords do not match'), 200
            return generate_response('Invalid password'), 200
        return generate_response('Invalid keys'), 400
    return generate_response('Provide JSON data'), 400

@AUTH.route('/bucketlists', methods=['POST', 'GET'])
@token_required
def bucketlists(the_user):
    """ Creates a bucketlist """
    if request.method == 'POST':
        new_bucketlist_json = request.get_json(silent=True)
        if new_bucketlist_json:
            if 'title' in new_bucketlist_json:
                existing_bucketlist = get_bucketlist(new_bucketlist_json['title'])
                if not existing_bucketlist:
                    a_bucketlist = Bucketlist(new_bucketlist_json['title'], the_user.identity)
                    DB.session.add(a_bucketlist)
                    DB.session.commit()
                    return generate_response('Bucketlist added'), 201
                return generate_response('Bucketlist already exists'), 400
            return generate_response('Invalid key in JSON data'), 400
        return generate_response('Provide proper JSON data'), 400
    if 'q' in request.args:
        title = request.args['q']
        searched_bucket = Bucketlist.query.filter_by(title=title).first()
        if searched_bucket:
            searched_bucket_dict = {
                'identity' : searched_bucket.identity,
                'title' : searched_bucket.title,
                'user_id' : searched_bucket.user_id
            }
            return generate_response(searched_bucket_dict), 200
        return generate_response('Bucket not found'), 404

    bucketlists_objs = the_user.bucketlists
    if bucketlists_objs:
        bucketlist_limit = 0
        bucketlist_count = 0
        if 'limit' in request.args:
            try:
                bucketlist_limit = int(request.args['limit'])
            except ValueError:
                return generate_response('Limit should be a positive integer')
        bucketlists_array = []
        for bucketlist_obj in bucketlists_objs:
            bucketlist_dict = {
                'identity' : bucketlist_obj.identity,
                'title' : bucketlist_obj.title,
                'user' : bucketlist_obj.user_id
            }
            bucketlists_array.append(bucketlist_dict)
            if bucketlist_limit > bucketlist_count:
                bucketlist_count += 1
                if bucketlist_limit == bucketlist_count:
                    break
        return generate_response(bucketlists_array), 200
    return generate_response('User has no buckets'), 404

@AUTH.route('/bucketlists/<identity>', methods=['GET', 'PUT', 'DELETE'])
@token_required
def bucketlist(the_user, identity):
    """ Returns a bucketlist whose ID has been provided """
    the_bucketlist = Bucketlist.query.filter_by(identity=identity).first()
    if the_bucketlist:
        if request.method == 'GET':
            obj = {
                'identity' : the_bucketlist.identity,
                'title' : the_bucketlist.title,
                'user id' : the_bucketlist.user_id
            }
            return generate_response(obj), 200
        elif request.method == 'PUT':
            update_bucketlist_json = request.get_json(silent=True)
            if update_bucketlist_json:
                if 'new_title' in update_bucketlist_json:
                    the_bucketlist.title = update_bucketlist_json['new_title']
                    DB.session.commit()
                    return generate_response('Bucketlist updated'), 200
                return generate_response('Invalid key in JSON data'), 400
            return generate_response('Provide proper JSON data'), 400
        else:
            DB.session.delete(the_bucketlist)
            DB.session.commit()
            return generate_response('Bucketlist deleted'), 200
    return generate_response('Bucketlist not found'), 404

@AUTH.route('/bucketlists/<bucket_identity>/items', methods=['POST', 'GET'])
@token_required
def items(the_user, bucket_identity):
    """ Creates a new Item """
    curr_bucketlist = Bucketlist.query.filter_by(identity=bucket_identity).first()
    if curr_bucketlist:
        if request.method == 'POST':
            new_item_json = request.get_json(silent=True)
            if new_item_json:
                if 'description' in new_item_json:
                    existing_item = Item.query.filter_by(
                        description=new_item_json['description']).first()
                    if not existing_item:
                        new_item = Item(new_item_json['description'], bucket_identity)
                        DB.session.add(new_item)
                        DB.session.commit()
                        return generate_response('Item created'), 200
                    return generate_response('Item already exists'), 404
                return generate_response('Invalid keys in JSON data'), 400
            return generate_response('Provide proper JSON data'), 400
        
        if 'q' in request.args:
            description = request.args['q']
            searched_item = Item.query.filter_by(description=description).first()
            if searched_item:
                searched_item_dict = {
                    'identity' : searched_item.identity,
                    'description' : searched_item.description,
                    'status' :searched_item.status,
                    'bucket_id' : searched_item.bucketlist_id
                }
                return generate_response(searched_item_dict), 200
            return generate_response('Bucket not found'), 404

        item_objs = curr_bucketlist.items
        if item_objs:
            items_array = []
            for item_obj in item_objs:
                item_dict = {
                    'identity' : item_obj.identity,
                    'description' : item_obj.description,
                    'status' : item_obj.status,
                    'bucketlist_id' : item_obj.bucketlist_id
                }
                items_array.append(item_dict)
            return generate_response(items_array), 200
        return generate_response('No items found')
    return generate_response('Bucketlist not found'), 404

@AUTH.route('/bucketlists/<bucket_identity>/items/<item_id>', methods=['PUT', 'DELETE'])
@token_required
def item(the_user, bucket_identity, item_id):
    """ Updates or deletes an Item """
    wor_bucketlist = Bucketlist.query.filter_by(identity=bucket_identity).first()
    if wor_bucketlist:
        cur_item = Item.query.filter_by(identity=item_id).first()
        if cur_item:
            if request.method == 'PUT':
                updt_item_json = request.get_json(silent=True)
                if updt_item_json:
                    if 'new_description' in updt_item_json and 'new_status' in updt_item_json:
                        cur_item.description = updt_item_json['new_description']
                        cur_item.status = updt_item_json['new_status']
                        DB.session.commit()
                        return generate_response('Item updated'), 200
                    return generate_response('Invalid keys in JSON data'), 400
                return generate_response('Provide proper JSON data'), 400

            DB.session.delete(cur_item)
            DB.session.commit()
            return generate_response('Item deleted'), 200
        return generate_response('Item not found'), 404
    return generate_response('Bucketlist not found'), 404

def generate_response(message):
    """ Creates a json response from provided message """
    response = {'message' : message}
    return jsonify(response)

def get_user(username):
    """ Returns a user object for provided username """
    return User.query.filter_by(username=username).first()

def get_bucketlist(title):
    """ Takes in a title and returns a bucketlist """
    return Bucketlist.query.filter_by(title=title).first()

APP.register_blueprint(AUTH, url_prefix='/auth')
