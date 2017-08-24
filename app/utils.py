from functools import wraps
from flask import jsonify, request
from app.models import LoggedoutToken, User
import jwt


def token_required(func):
    """ Defines a decorator for views requiring token authentication """
    @wraps(func)
    def decorated(*args, **kwargs):
        """ Defines the decorated function """
        if 'x-access-token' in request.headers:
            received_token = request.headers['x-access-token']
            if LoggedoutToken.query.filter_by(token=received_token).first():
                response = {
                    'status': 'Error',
                    'message': 'Your token is expired. Please login to get a new token.'
                }
                return jsonify(response), 401
            else:
                try:
                    token_data = jwt.decode(received_token, '254HHSY18836')
                    the_user = User.query.filter_by(
                        username=token_data['username']).first()
                    if the_user:
                        return func(the_user, *args, **kwargs)
                    response = {
                        'status': 'Error',
                        'message': 'Sorry, the username ' +
                        token_data['username'] + ' was not found'
                    }
                    return jsonify(response), 404
                except jwt.ExpiredSignatureError:
                    response = {
                        'status': 'Error',
                        'message': 'Sorry, the token you provided is ' +
                        'expired. Please login to get another'
                    }
                    return jsonify(response), 498
                except jwt.InvalidTokenError:
                    response = {
                        'status': 'Error',
                        'message': 'Sorry, the token you provided is invalid'
                    }
                    return jsonify(response), 498
        response = {
            'status': 'Error',
            'message': 'Please provide a token with a key x-access-token'
        }
        return jsonify(response), 401
    return decorated


def get_json_input():
    """ Converts user input into a JSON object """
    # silent attribute ensures None is returned and no exception is thrown if get_json fails
    input_json_data = request.get_json(silent=True)
    if input_json_data:
        return input_json_data

    response_data = {
        'status': 'Error',
        'message': 'Input data should be in JSON format'
    }
    return jsonify(response_data), 400