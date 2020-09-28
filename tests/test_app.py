import json
import unittest
from unittest.mock import patch
from tests import db_drop_everything, assert_payload_field_type_value
from api import create_app, db


class AppTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db_drop_everything(db)
        self.app_context.pop()

    def test_cors(self):
        response = self.client.head('/')

        assert_payload_field_type_value(
            self,
            response.headers,
            'Access-Control-Allow-Origin',
            str,
            '*'
        )
        assert_payload_field_type_value(
            self,
            response.headers,
            'Access-Control-Allow-Headers',
            str,
            'Content-Type'
        )
        assert_payload_field_type_value(
            self,
            response.headers,
            'Access-Control-Allow-Methods',
            str,
            'GET, PATCH, POST, DELETE, OPTIONS'
        )

    def test_home_page_content(self):
        response = self.client.get('/')

        self.assertIn(b'Login', response.data)

    @patch('api.auth.auth.check_permissions')
    @patch('api.auth.auth.verify_decode_jwt')
    @patch('api.auth.auth.get_token_auth_header')
    def test_mock_auth_required_success(
            self,
            mock_get_token_auth_header,
            mock_verify_decode_jwt,
            mock_check_permissions):
        mock_get_token_auth_header.return_value = 'token-abc123'
        mock_verify_decode_jwt.return_value = {
            'permissions': ['get:roadtrips']
        }
        mock_check_permissions.return_value = True

        response = self.client.get(
            '/auth-required',
            headers={}
        )
        self.assertEqual(200, response.status_code)

    @patch('api.auth.auth.verify_decode_jwt')
    @patch('api.auth.auth.get_token_auth_header')
    def test_mock_auth_required_bad_perm(
            self,
            mock_get_token_auth_header,
            mock_verify_decode_jwt):
        mock_get_token_auth_header.return_value = 'token-abc123'
        mock_verify_decode_jwt.return_value = {
            'permissions': ['get:nothing']
        }

        response = self.client.get(
            '/auth-required',
            headers={'Authorization': 'Bearer foo'}
        )
        self.assertEqual(403, response.status_code)
        data = json.loads(response.data.decode('utf-8'))

        assert_payload_field_type_value(
            self, data, 'message', str, 'forbidden'
        )
        assert_payload_field_type_value(
            self, data, 'success', bool, False
        )
        assert_payload_field_type_value(
            self, data, 'error', int, 403
        )
