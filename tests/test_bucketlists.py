from .test_base import TestBase, db, Bucketlist
import unittest
from flask import json


class TestBucketlist(TestBase):
    """ Defines tests for the view methods of bucketlists """

    def setUp(self):
        self.create_valid_user()

    def test_accessing_bucketlist_view_without_token(self):
        """ Tests accessing the bucketlist endpoint without a token """
        response = self.client.get('/bucketlists')
        self.assertEqual(response.status_code, 401)

    def test_accessing_bucketlist_view_with_invalid_or_expired_token(self):
        """ Tests accessing the bucketlist endpoint with an invalid
        or expired token """
        response = self.client.get('/bucketlists',
                                   headers={'x-access-token':
                                            'XBA5567SJ2K119'})
        self.assertEqual(response.status_code, 498)

    def test_create_bucketlist_with_valid_details(self):
        """ Tests adding a bucketlist with valid details """
        response = self.create_valid_bucket()
        self.assertEqual(response.status_code, 201)
        self.delete_valid_bucket()

    def test_create_bucketlist_with_non_json_input(self):
        """ Tests adding a bucketlist with non valid json input """
        response = self.client.post('/bucketlists', data=self.non_json_data,
                                    content_type='application/json',
                                    headers={'x-access-token':
                                             self.get_token()})
        self.assertEqual(response.status_code, 400)

    def test_create_bucketlist_with_invalid_json_attributes(self):
        """ Tests adding a bucketlist with invalid json attributes """
        response = self.client.post('/bucketlists',
                                    data=json.dumps(self.wrong_keys_data),
                                    content_type='application/json',
                                    headers={'x-access-token':
                                             self.get_token()})
        self.assertEqual(response.status_code, 400)

    def test_create_bucketlist_with_blank_attributes(self):
        """ Tests creating a bucketlist with a blank title or description """
        bucketlist = {
            'title': '',
            'description': ''
        }
        response = self.client.post('/bucketlists',
                                    data=json.dumps(bucketlist),
                                    content_type='application/json',
                                    headers={'x-access-token':
                                             self.get_token()})
        self.assertEqual(response.status_code, 400)

    def test_create_duplicate_bucketlist(self):
        """ Tests creating a duplicate bucketlist (same title) """
        self.create_valid_bucket()
        response = self.create_valid_bucket()
        self.assertEqual(response.status_code, 400)
        self.delete_valid_bucket()

    def test_search_bucketlist_with_valid_title(self):
        """ Tests searching for a valid bucketlist by it's title """
        self.create_valid_bucket()
        response = self.client.get('/bucketlists?q=' +
                                   self.valid_bucketlist['title'],
                                   headers={'x-access-token':
                                            self.get_token()})
        self.assertEqual(response.status_code, 200)
        self.delete_valid_bucket()

    def test_search_non_existent_bucketlist(self):
        """ Tests searching for a non existent bucketlist """
        bucketlist = {
            'title': 'Fake Title',
            'description': 'The Description'
        }
        response = self.client.get('/bucketlists?q='+bucketlist['title'],
                                   headers={'x-access-token':
                                            self.get_token()})
        self.assertEqual(response.status_code, 404)

    def test_get_bucketlists(self):
        """ Tests querying all bucketlists for a user """
        self.create_valid_bucket()
        response = self.client.get('/bucketlists',
                                   headers={'x-access-token':
                                            self.get_token()})
        self.assertEqual(response.status_code, 200)
        self.delete_valid_bucket()

    def test_get_bucketlists_with_valid_limit(self):
        """ Tests querying bucketlists with a valid limit for number of
        results """
        self.create_valid_bucket()
        response = self.client.get('/bucketlists?limit=2',
                                   headers={'x-access-token':
                                            self.get_token()})
        self.assertEqual(response.status_code, 200)
        self.delete_valid_bucket()

    def test_get_bucketlists_with_non_numeric_limit(self):
        """ Tests querying bucketlists with a limit for number of
        results that isn't a number """
        response = self.client.get('/bucketlists?limit=ab',
                                   headers={'x-access-token':
                                            self.get_token()})
        self.assertEqual(response.status_code, 404)

    def test_get_bucketlists_for_a_user_without_any_bucketlists(self):
        """ Tests querying for bucketlists for a user that has none """
        response = self.client.get('/bucketlists',
                                   headers={'x-access-token':
                                            self.get_token()})
        self.assertEqual(response.status_code, 404)

    def test_get_bucketlists_valid_id(self):
        """ Tests querying a bucketlists by a valid ID """
        response = self.create_valid_bucket()
        data = json.loads(response.data.decode())
        response = self.client.get('/bucketlists/' +
                                   str(data['bucketlist']['id']),
                                   headers={'x-access-token':
                                            self.get_token()})
        self.assertEqual(response.status_code, 200)
        self.delete_valid_bucket()

    def test_bucketlists_view_with_invalid_id(self):
        """ Tests querying for a bucketlist with a none existent ID """
        response = self.client.get('/bucketlists/1',
                                   headers={'x-access-token':
                                            self.get_token()})
        self.assertEqual(response.status_code, 404)

    def test_update_bucketlist_with_valid_details(self):
        """ Tests updating a bucketlist with proper details provided """
        response = self.create_valid_bucket()
        data = json.loads(response.data.decode())
        response = self.client.put('/bucketlists/' +
                                   str(data['bucketlist']['id']),
                                   data=json.dumps(self.valid_bucketlist),
                                   content_type='application/json',
                                   headers={'x-access-token':
                                            self.get_token()})
        self.assertEqual(response.status_code, 200)
        self.delete_valid_bucket()

    def test_update_bucketlist_with_invalid_details(self):
        """ Tests updating a bucketlist with wrong details provided """
        response = self.create_valid_bucket()
        data = json.loads(response.data.decode())
        response = self.client.put('/bucketlists/' +
                                   str(data['bucketlist']['id']),
                                   data=json.dumps(self.wrong_keys_data),
                                   content_type='application/json',
                                   headers={'x-access-token':
                                            self.get_token()})
        self.assertEqual(response.status_code, 400)
        self.delete_valid_bucket()

    def test_update_bucketlist_with_non_json_data(self):
        """ Tests updating a bucketlist with non JSON input """
        response = self.create_valid_bucket()
        data = json.loads(response.data.decode())
        response = self.client.put('/bucketlists/' +
                                   str(data['bucketlist']['id']),
                                   data=json.dumps(self.non_json_data),
                                   content_type='application/json',
                                   headers={'x-access-token':
                                            self.get_token()})
        self.assertEqual(response.status_code, 400)
        self.delete_valid_bucket()

    def test_delete_bucket(self):
        """ Tests deleting a bucketlist """
        response = self.create_valid_bucket()
        data = json.loads(response.data.decode())
        response = self.client.delete('/bucketlists/' +
                                      str(data['bucketlist']['id']),
                                      headers={'x-access-token':
                                               self.get_token()})
        self.assertEqual(response.status_code, 200)

    def tearDown(self):
        self.delete_valid_user()

if __name__ == '__main__':
    unittest.main()
