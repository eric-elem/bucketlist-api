from test_base import TestBase
import unittest
from flask import json


class TestBucketlist(TestBase):
    def test_create_bucketlist_valid_details(self):
        """ Tests adding a bucketlist with valid details """
        data = {
            'title': 'thetestbucketlist',
        }
        response = APP.test_client().post('/auth/bucketlists',
                                          data=json.dumps(data),
                                          content_type='application/json',
                                          headers={'x-access-token':
                                                   self.get_token()})
        self.assertEqual(response.status_code, 201)

    def test_create_bucketlist_non_json_input(self):
        """ Tests adding a bucketlist with non valid json input """
        response = APP.test_client().post('/auth/bucketlists',
                                          data=self.non_json_data,
                                          content_type='application/json',
                                          headers={'x-access-token':
                                                   self.get_token()})
        self.assertEqual(response.status_code, 400)

    def test_create_bucketlist_invalid_json_keys(self):
        """ Tests adding a bucketlist with invalid json keys """
        response = APP.test_client().post('/auth/bucketlists',
                                          data=json.dumps(self.wrong_keys_data)
                                          , content_type='application/json',
                                          headers={'x-access-token':
                                                   self.get_token()})
        self.assertEqual(response.status_code, 400)
        