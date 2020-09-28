import json
import unittest

from api import create_app, db
from tests import db_drop_everything, assert_payload_field_type_value


class ErrorsTest(unittest.TestCase):
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

    def test_404_error(self):
        response = self.client.get('/lkjasdkj')

        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data.decode('utf-8'))

        assert_payload_field_type_value(
            self, data, 'message', str, 'resource not found'
        )
        assert_payload_field_type_value(self, data, 'error', int, 404)
        assert_payload_field_type_value(self, data, 'success', bool, False)

    def test_401_error_no_auth_header(self):
        response = self.client.get('/auth-required', headers={})
        self.assertEqual(response.status_code, 401)

        data = json.loads(response.data.decode('utf-8'))
        assert_payload_field_type_value(
            self, data, 'message', str, 'unauthorized'
        )
        assert_payload_field_type_value(
            self, data, 'success', bool, False
        )

    def test_401_error_empty_auth_header(self):
        response = self.client.get(
            '/auth-required',
            headers={'Authorization': '.'}
        )
        self.assertEqual(response.status_code, 401)

        data = json.loads(response.data.decode('utf-8'))
        assert_payload_field_type_value(
            self, data, 'message', str, 'unauthorized'
        )
        assert_payload_field_type_value(
            self, data, 'success', bool, False
        )

    def test_401_error_empty_auth_bearer(self):
        response = self.client.get(
            '/auth-required',
            headers={'Authorization': 'Bearer'}
        )
        self.assertEqual(response.status_code, 401)

        data = json.loads(response.data.decode('utf-8'))
        assert_payload_field_type_value(
            self, data, 'message', str, 'unauthorized'
        )
        assert_payload_field_type_value(
            self, data, 'success', bool, False
        )

    def test_401_error_bad_auth_bearer(self):
        response = self.client.get(
            '/auth-required',
            headers={'Authorization': 'Bearer foo'}
        )
        self.assertEqual(response.status_code, 401)

        data = json.loads(response.data.decode('utf-8'))
        assert_payload_field_type_value(
            self, data, 'message', str, 'unauthorized'
        )
        assert_payload_field_type_value(
            self, data, 'success', bool, False
        )

    def test_401_error_auth_bearer_too_big(self):
        response = self.client.get(
            '/auth-required',
            headers={'Authorization': 'Bearer foo baz'}
        )
        self.assertEqual(response.status_code, 401)

        data = json.loads(response.data.decode('utf-8'))
        assert_payload_field_type_value(
            self, data, 'message', str, 'unauthorized'
        )
        assert_payload_field_type_value(
            self, data, 'success', bool, False
        )
