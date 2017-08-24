from test_base import TestBase
import unittest
from flask import json

class TestAuth(TestBase):
    def test_register_valid_details(self):
        """ Tests creating a new user with valid details """
        data = {
            'name': 'A new user',
            'username': 'anewuser',
            'password': 'password',
            'password_rpt': 'password'
        }
        response = self.client.post('/auth/register', data=json.dumps(data),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 201)

    def test_register_non_json_input(self):
        """ Tests register with non valid json input """
        response = self.client.post('/auth/register', data=self.non_json_data,
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_register_invalid_json_keys(self):
        """ Tests register with invalid json keys """
        response = self.client.post('/auth/register',
                                    data=json.dumps(self.wrong_keys_data),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_register_unmatch_passwords(self):
        """ Tests creating a new user with valid details """
        data = {
            'name': 'A new user',
            'username': 'newuser',
            'password': 'password',
            'password_rpt': 'new_password'
        }
        response = self.client.post('/auth/register', data=json.dumps(data),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_register_existing_user(self):
        """ Tests creating a new user with existing username """
        data = {
            'name': 'A new user',
            'username': 'anewuser',
            'password': 'password',
            'password_rpt': 'password'
        }
        response = self.client.post('/auth/register', data=json.dumps(data),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 201)
        response = self.client.post('/auth/register', data=json.dumps(data),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 202)

    def test_login_valid_credentials(self):
        """ Tests login with valid credentials """
        data = {
            'username': self.user.username,
            'password': self.raw_password
        }
        response = self.client.post('/auth/login', data=json.dumps(data),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        ret_json_data = json.loads(response.data.decode())
        self.assertTrue(ret_json_data['token'])

    def test_login_non_json_input(self):
        """ Tests login with non valid json input """
        response = self.client.post('/auth/login', data=self.non_json_data,
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_login_invalid_json_keys(self):
        """ Tests login with invalid json keys """
        response = self.client.post('/auth/login',
                                    data=json.dumps(self.wrong_keys_data),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_login_invalid_username(self):
        """ Tests login with invalid username """
        data = {
            'username': self.invalid_username,
            'password': self.raw_password
        }
        response = self.client.post('/auth/login', data=json.dumps(data),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_login_invalid_password(self):
        """ Tests login with invalid password """
        data = {
            'username': self.user.username,
            'password': self.invalid_password
        }
        response = self.client.post('/auth/login', data=json.dumps(data),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 401)

    def test_rst_password_valid_details(self):
        """ Tests resetting a password with valid details """
        data = {
            'password': 'password',
            'new_password': 'new_password',
            'new_password_rpt': 'new_password'
        }
        response = self.client.post('/auth/reset-password',
                                    data=json.dumps(data),
                                    content_type='application/json',
                                    headers={'x-access-token': self.get_token()})
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
