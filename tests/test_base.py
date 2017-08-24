""" Tests module """
import unittest

import sys
sys.path.append('./')
from flask import json
from app import create_app, db
from app.models import User, Bucketlist


class TestBase(unittest.TestCase):
    """ Tests view methods """

    def setUp(self):
        app = create_app('TESTING')
        app.app_context().push()
        self.client = app.test_client()
        self.raw_password = 'password'
        self.invalid_password = 'invalid_password'
        self.invalid_username = 'invalid_username'
        self.user = User('theuser', self.raw_password, 'Test User')
        db.session.add(self.user)
        db.session.commit()
        self.non_json_data = 'some data'
        self.wrong_keys_data = {
            "wrong": "Eric",
            "key": 51
        }

    def get_token(self):
        data = {
            'username': self.user.username,
            'password': self.raw_password
        }
        response = self.client.post('/auth/login', data=json.dumps(data),
                                          content_type='application/json')
        ret_json_data = json.loads(response.data.decode())
        return ret_json_data['token']

    def tearDown(self):
        db.session.query(User).filter_by(username='anewuser').delete()
        db.session.query(
            Bucketlist).filter_by(title='thetestbucketlist').delete()
        db.session.delete(self.user)
        db.session.commit()

