from test_base import TestBase, db, User
import unittest
from flask import json


class TestAuth(TestBase):
    def test_register_valid_details(self):
        """ Tests creating a new user with valid details """
        user = {
            'name': 'test user',
            'username': 'user',
            'password': 'password',
            'password_rpt': 'password'
        }
        response = self.client.post('/auth/register',
                                    data=json.dumps(user),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 201)
        db.session.query(User).\
            filter_by(username=user['username']).delete()
        db.session.commit()

    def test_register_non_json_input(self):
        """ Tests register with non valid JSON input """
        response = self.client.post('/auth/register', data=self.non_json_data,
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_register_invalid_json_keys(self):
        """ Tests register with invalid attributes provided """
        response = self.client.post('/auth/register',
                                    data=json.dumps(self.wrong_keys_data),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_register_blank_values(self):
        """ Tests register with blank attribute values provided """
        user = {
            'name': '',
            'username': '',
            'password': '',
            'password_rpt': ''
        }
        response = self.client.post('/auth/register',
                                    data=json.dumps(user),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_register_unmatch_passwords(self):
        """ Tests creating a new user with unmatching passwords """
        user = {
            'name': 'New User',
            'username': 'newuser',
            'password': 'password',
            'password_rpt': 'new_password'
        }
        response = self.client.post('/auth/register', data=json.dumps(user),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_register_existing_user(self):
        """ Tests creating a new user with existing username """
        self.create_valid_user()
        response = self.create_valid_user()
        self.assertEqual(response.status_code, 202)
        self.delete_valid_user()

    def test_login_valid_credentials(self):
        """ Tests login with valid credentials """
        self.create_valid_user()
        user = {
            'username': 'testuser',
            'password': 'password'
        }
        response = self.client.post('/auth/login', data=json.dumps(user),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode())
        self.assertTrue(data['token'])
        self.delete_valid_user()

    def test_login_non_json_input(self):
        """ Tests login with non JSON input """
        response = self.client.post('/auth/login', data=self.non_json_data,
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_login_invalid_json_keys(self):
        """ Tests login with invalid attributes """
        response = self.client.post('/auth/login',
                                    data=json.dumps(self.wrong_keys_data),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_login_invalid_username(self):
        """ Tests login with invalid username """
        self.create_valid_user()
        user = {
            'username': 'user',
            'password': 'password'
        }
        response = self.client.post('/auth/login', data=json.dumps(user),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 404)
        self.delete_valid_user()

    def test_login_invalid_password(self):
        """ Tests login with invalid password """
        self.create_valid_user()
        user = {
            'username': 'testuser',
            'password': 'pass'
        }
        response = self.client.post('/auth/login', data=json.dumps(user),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 401)
        self.delete_valid_user()

    def test_reset_password_valid_details(self):
        """ Tests resetting a password with valid details """
        data = {
            'password': 'password',
            'new_password': 'new_password',
            'new_password_rpt': 'new_password'
        }
        response = self.client.post('/auth/reset-password',
                                    data=json.dumps(data),
                                    content_type='application/json',
                                    headers={'x-access-token':
                                             self.get_token()})
        self.assertEqual(response.status_code, 200)

    def test_rst_password_non_json_input(self):
        """ Tests resetting password with non valid json input """
        response = self.client.post('/auth/reset-password',
                                    data=self.non_json_data,
                                    content_type='application/json',
                                    headers={'x-access-token': self.get_token()})
        self.assertEqual(response.status_code, 400)

    def test_rst_password_invalid_json_keys(self):
        """ Tests resetting password with invalid json keys """
        response = self.client.post('/auth/reset-password',
                                    data=json.dumps(self.wrong_keys_data),
                                    content_type='application/json',
                                    headers={'x-access-token': self.get_token()})
        self.assertEqual(response.status_code, 400)

    def test_rst_password_wrong_password(self):
        """ Tests resetting password with wrong current password """
        data = {
            'password': 'mypassword',
            'new_password': 'password',
            'new_password_rpt': 'password'
        }
        response = self.client.post('/auth/reset-password',
                                    data=json.dumps(data),
                                    content_type='application/json',
                                    headers={'x-access-token': self.get_token()})
        self.assertEqual(response.status_code, 200)

    def test_rst_password_unmatch_passwords(self):
        """ Tests resetting password with unmatching new passwords """
        data = {
            'password': 'password',
            'new_password': 'password',
            'new_password_rpt': 'new_password'
        }
        response = self.client.post('/auth/reset-password',
                                    data=json.dumps(data),
                                    content_type='application/json',
                                    headers={'x-access-token': self.get_token()})
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
