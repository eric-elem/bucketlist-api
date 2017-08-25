""" Applications view methods """

import datetime
import jwt
from flask import Blueprint, request, jsonify
from app.models import db, User, Bucketlist, Item, LoggedoutToken
from app.utils import get_json_input, token_required

auth = Blueprint('auth', __name__)


@auth.route('/register', methods=['POST'])
def register():
    """ Creates an account for a new user """
    data = get_json_input()
    if 'name' in data and 'username' in data and 'password'\
            in data and 'password_rpt' in data:
        if len(data['name']) or len(data['username']) or len(data['password'])\
                or len(data['password']) or len(data['password_rpt']):
            try:
                int(data['username'])
                response = {
                    'status': 'Error',
                    'message': 'Username should not consist of numbers only'
                }
                return jsonify(response), 400
            except:
                if data['password'] == data['password_rpt']:
                    user = User.query.filter_by(username=data['username'])\
                        .first()
                    if not user:
                        newuser = User(data['username'], data['password'],
                                       data['name'])
                        db.session.add(newuser)
                        db.session.commit()
                        response = {
                            'status': 'Success',
                            'message': 'The user '+newuser.name+' has been created',
                            'user': {
                                'id': newuser.user_id,
                                'name': newuser.name,
                                'username': newuser.username,
                                'created_at': newuser.created_at
                            }
                        }
                        return jsonify(response), 201
                    response = {
                        'status': 'Error',
                        'message': 'A user with the username ' +
                        data['username'] + ' already exists'
                    }
                    return jsonify(response), 202
                response = {
                    'status': 'Error',
                    'message': "The provided passwords 'password' and " +
                    "'password_rpt' must match"
                }
                return jsonify(response), 400
            response = {
                'status': 'Error',
                'message': "Attributes name, username, " +
                "password, and/or password_rpt cannot be blank"
            }
            return jsonify(response), 400
    response = {
        'status': 'Error',
        'message': "Please provide all the attributes 'name', 'username', " +
        "'password', and 'password_rpt' for the new user"
    }
    return jsonify(response), 400


@auth.route('/login', methods=['POST'])
def login():
    """ Handles signing in users """
    credentials = get_json_input()
    if 'username' in credentials and 'password' in credentials:
        user = User.query.filter_by(username=credentials['username']).first()
        if user:
            if user.verify_password(credentials['password']):
                db.session.query(LoggedoutToken).\
                    filter_by(user_id=user.user_id).delete()
                db.session.commit()
                token = jwt.encode({'username': credentials['username'],
                                    'exp': datetime.datetime.utcnow() +
                                    datetime.timedelta(minutes=60)},
                                   '254HHSY18836')
                response = {
                    'status': 'Success',
                    'message': 'You have logged in ' + user.name,
                    'token': token.decode('UTF-8')
                }
                return jsonify(response), 200
            response = {
                'status': 'Error',
                'message': 'Sorry, the provided password is incorrect'
            }
            return jsonify(response), 401
        response = {
            'status': 'Error',
            'message': 'User ' + credentials['username'] + ' does not exist'
        }
        return jsonify(response), 404
    response = {
        'status': 'Error',
        'message': "Please provide a username and password"
    }
    return jsonify(response), 400


@auth.route('/logout')
@token_required
def logout(the_user):
    """ Handles user logout """
    users_token = request.headers['x-access-token']
    logged_out_token = LoggedoutToken(users_token, the_user.user_id)
    db.session.add(logged_out_token)
    db.session.commit()
    response = {
        'status': 'success',
        'message': 'You have been logged out ' + the_user.name
    }
    return jsonify(response), 200


@auth.route('/reset-password', methods=['POST'])
@token_required
def reset_password(the_user):
    """ Updates users password """
    user = get_json_input()
    if ('password' in user and
            'new_password' in user and
            'new_password_rpt' in user):
        if the_user.verify_password(user['password']):
            if user['new_password'] == \
                    user['new_password_rpt']:
                the_user.set_password(user['new_password'])
                db.session.add(the_user)
                db.session.commit()
                response = {
                    'status': 'Error',
                    'message': 'Your password has been updated ' + 
                    the_user.name
                }
                return jsonify(response), 200
            response = {
                'status': 'Error',
                'message': 'The new passwords you provided do not match'
            }
            return jsonify(response), 200
        response = {
            'status': 'Error',
            'message': 'The current password you provided is wrong'
        }
        return jsonify(response), 200
    response = {
        'status': 'Error',
        'message': "Please provide all attributes 'password', 'new_password', " +
        "and 'new_password_rpt'"
    }
    return jsonify(response), 400


@auth.errorhandler(404)
def handle_error_404(error):
    response = {
        'status': 'Error',
        'message': 'Request not found'
    }
    return jsonify(response), 404
