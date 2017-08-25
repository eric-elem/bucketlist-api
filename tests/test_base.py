""" Tests module """
import unittest

import sys
sys.path.append('./')
from flask import json
from app.models import User, Bucketlist, Item

from app import create_app, db

class TestBase(unittest.TestCase):
    """ Base class for all test classess """

    app = create_app('TESTING')
    app.app_context().push()

    client = app.test_client()

    username = 'user'
    password = 'password'
    name = 'User'
    user = User(username, password, name)

    bucketlist_title = 'Bucket Title'
    bucketlist_description = 'Bucketlist Description'

    item_title = 'Item Title'
    item_description = 'Item Description'

    non_json_data = 'some non json data'
    wrong_keys_data = {
        "wrong": "Value",
        "key": "Value"
    }

    valid_user = {
        'name': 'Test User',
        'username': 'testuser',
        'password': 'password',
        'password_rpt': 'password'
    }

    valid_bucketlist = {
        'title': 'The Title',
        'description': 'The Description'
    }

    valid_item = {
        'title': 'The Title',
        'description': 'The Description'
    }

    def setUp(self):
        self.create_valid_user()

    def create_valid_user(self):
        response = self.client.post('/auth/register', 
                                    data=json.dumps(self.valid_user),
                                    content_type='application/json')
        return response

    def delete_valid_user(self):
        db.session.query(User).\
            filter_by(username=self.valid_user['username']).delete()
        db.session.commit()

    def get_token(self):
        response = self.client.post('/auth/login',
                                    data=json.dumps(self.valid_user),
                                    content_type='application/json')
        data = json.loads(response.data.decode())
        return data['token']

    def create_valid_bucket(self):
        """ Creates a valid bucketlist to be used for tests """
        response = self.client.post('/bucketlists',
                                    data=json.dumps(self.valid_bucketlist),
                                    content_type='application/json',
                                    headers={'x-access-token':
                                             self.get_token()})
        return response

    def delete_valid_bucket(self):
        """ Deletes the valid bucket after tests """
        db.session.query(Bucketlist).\
            filter_by(title=self.valid_bucketlist['title']).delete()
        db.session.commit()

    def create_valid_item(self):
        """ Creates a valid item to be used for tests """
        response = self.client.post('/bucketlists/' + self.bucketlist_id +
                                    '/items', data=json.dumps(self.valid_item),
                                    content_type='application/json',
                                    headers={'x-access-token':
                                             self.get_token()})
        return response

    def delete_valid_item(self):
        """ Deletes the valid item after tests """
        db.session.query(Item).\
            filter_by(title=self.valid_item['title']).delete()
        self.delete_valid_bucket()

    def tearDown(self):
        self.delete_valid_user()
