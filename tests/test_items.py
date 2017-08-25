from test_base import TestBase, db, Bucketlist
import unittest
from flask import json


class TestItems(TestBase):
    """ Defines tests for the view methods of items """

    def setUp(self):
        self.create_valid_user()
        response = self.create_valid_bucket()
        data = json.loads(response.data.decode())
        self.bucketlist_id = str(data['bucketlist']['id'])


    def test_accessing_items_view_without_token(self):
        """ Tests accessing the items endpoint without a token """
        response = self.client.get('/bucketlists/' + self.bucketlist_id +
                                   '/items')
        self.assertEqual(response.status_code, 401)

    def test_accessing_items_view_with_invalid_or_expired_token(self):
        """ Tests accessing the items endpoint with an invalid
        or expired token """
        response = self.client.get('/bucketlists/' + self.bucketlist_id +
                                   '/items', headers={'x-access-token':
                                                      'XBA5567SJ2K119'})
        self.assertEqual(response.status_code, 498)

    def test_create_item_with_valid_details(self):
        """ Tests adding an item with valid details """
        response = self.create_valid_item()
        self.assertEqual(response.status_code, 201)
        self.delete_valid_item()

    def test_create_item_with_non_json_input(self):
        """ Tests adding an item with non valid json input """
        response = self.client.post('/bucketlists/' + self.bucketlist_id +
                                    '/items', data=self.non_json_data,
                                    content_type='application/json',
                                    headers={'x-access-token':
                                             self.get_token()})
        self.assertEqual(response.status_code, 400)

    def test_create_item_with_invalid_json_attributes(self):
        """ Tests adding an item with invalid json attributes """
        response = self.client.post('/bucketlists/' + self.bucketlist_id +
                                    '/items',
                                    data=json.dumps(self.wrong_keys_data),
                                    content_type='application/json',
                                    headers={'x-access-token':
                                             self.get_token()})
        self.assertEqual(response.status_code, 400)

    def test_create_item_with_blank_attributes(self):
        """ Tests creating an item with a blank title or description """
        item = {
            'title': '',
            'description': ''
        }
        response = self.client.post('/bucketlists/' + self.bucketlist_id +
                                    '/items', data=json.dumps(item),
                                    content_type='application/json',
                                    headers={'x-access-token':
                                             self.get_token()})
        self.assertEqual(response.status_code, 400)

    def test_create_duplicate_item(self):
        """ Tests creating a duplicate item (same title) """
        self.create_valid_item()
        response = self.create_valid_item()
        self.assertEqual(response.status_code, 404)
        self.delete_valid_item()

    def test_search_item_with_valid_title(self):
        """ Tests searching for a valid item by it's title """
        self.create_valid_item()
        response = self.client.get('/bucketlists/' + self.bucketlist_id +
                                   '/items?q=' +
                                   self.valid_item['title'],
                                   headers={'x-access-token':
                                            self.get_token()})
        self.assertEqual(response.status_code, 200)
        self.delete_valid_item()

    def test_search_non_existent_item(self):
        """ Tests searching for a non existent item """
        item = {
            'title': 'Fake Title',
            'description': 'The Description'
        }
        response = self.client.get('/bucketlists/' + self.bucketlist_id +
                                   '/items?q=' + item['title'],
                                   headers={'x-access-token':
                                            self.get_token()})
        self.assertEqual(response.status_code, 404)

    def test_get_items(self):
        """ Tests querying all items in a bucket """
        self.create_valid_item()
        response = self.client.get('/bucketlists/' + self.bucketlist_id +
                                   '/items', headers={'x-access-token':
                                                      self.get_token()})
        self.assertEqual(response.status_code, 200)
        self.delete_valid_item()

    def test_get_items_with_valid_limit(self):
        """ Tests querying items with a valid limit for number of
        results """
        self.create_valid_item()
        response = self.client.get('/bucketlists/' + self.bucketlist_id +
                                   '/items?limit=2',
                                   headers={'x-access-token':
                                            self.get_token()})
        self.assertEqual(response.status_code, 200)
        self.delete_valid_item()

    def test_get_items_with_non_numeric_limit(self):
        """ Tests querying items with a limit for number of
        results that isn't a number """
        response = self.client.get('/bucketlists/' + self.bucketlist_id +
                                   '/items?limit=ab',
                                   headers={'x-access-token':
                                            self.get_token()})
        self.assertEqual(response.status_code, 404)

    def test_get_items_for_a_user_without_any_items(self):
        """ Tests querying for items for a user that has none """
        response = self.client.get('/bucketlists/' + self.bucketlist_id +
                                   '/items', headers={'x-access-token':
                                                      self.get_token()})
        self.assertEqual(response.status_code, 404)

    def test_get_items_valid_id(self):
        """ Tests querying an item by a valid ID """
        response = self.create_valid_item()
        data = json.loads(response.data.decode())
        response = self.client.get('/bucketlists/' + self.bucketlist_id +
                                   '/items/' +
                                   str(data['item']['id']),
                                   headers={'x-access-token':
                                            self.get_token()})
        self.assertEqual(response.status_code, 200)
        self.delete_valid_item()

    def test_items_view_with_invalid_id(self):
        """ Tests querying for an item with a none existent ID """
        response = self.client.get('/bucketlists/' + self.bucketlist_id +
                                    '/items/1',
                                   headers={'x-access-token':
                                            self.get_token()})
        self.assertEqual(response.status_code, 404)

    def test_update_items_with_valid_details(self):
        """ Tests updating an item with proper details provided """
        response = self.create_valid_item()
        data = json.loads(response.data.decode())
        response = self.client.put('/bucketlists/' + self.bucketlist_id +
                                   '/items/' +
                                   str(data['item']['id']),
                                   data=json.dumps(self.valid_bucketlist),
                                   content_type='application/json',
                                   headers={'x-access-token':
                                            self.get_token()})
        self.assertEqual(response.status_code, 200)
        self.delete_valid_item()

    def test_update_item_with_invalid_details(self):
        """ Tests updating an item with wrong details provided """
        response = self.create_valid_item()
        data = json.loads(response.data.decode())
        response = self.client.put('/bucketlists/' + self.bucketlist_id +
                                   '/items/' +
                                   str(data['item']['id']),
                                   data=json.dumps(self.wrong_keys_data),
                                   content_type='application/json',
                                   headers={'x-access-token':
                                            self.get_token()})
        self.assertEqual(response.status_code, 400)
        self.delete_valid_item()

    def test_update_item_with_non_json_data(self):
        """ Tests updating an item with non JSON input """
        response = self.create_valid_item()
        data = json.loads(response.data.decode())
        response = self.client.put('/bucketlists/' + self.bucketlist_id +
                                   '/items/' +
                                   str(data['item']['id']),
                                   data=json.dumps(self.non_json_data),
                                   content_type='application/json',
                                   headers={'x-access-token':
                                            self.get_token()})
        self.assertEqual(response.status_code, 400)
        self.delete_valid_item()

    def test_delete_item(self):
        """ Tests deleting an item """
        response = self.create_valid_item()
        data = json.loads(response.data.decode())
        response = self.client.delete('/bucketlists/' + self.bucketlist_id +
                                      '/items/' +
                                      str(data['item']['id']),
                                      headers={'x-access-token':
                                               self.get_token()})
        self.assertEqual(response.status_code, 200)

    def tearDown(self):
        self.delete_valid_item()
        self.delete_valid_user()

if __name__ == '__main__':
    unittest.main()
