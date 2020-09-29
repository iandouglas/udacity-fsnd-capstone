import json
import unittest
from copy import deepcopy
from unittest.mock import patch

from api import create_app, db
from tests import db_drop_everything, assert_payload_field_type_value, \
    assert_payload_field_type


class CreateRoadtripTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()
        self.payload = {
            'name': 'commute',
            'start_city': 'Arvada, CO',
            'end_city': 'Denver, CO'
        }

    def tearDown(self):
        db.session.remove()
        db_drop_everything(db)
        self.app_context.pop()


class GuestUserTest(CreateRoadtripTest):
    def test_endpoint_badauth_create_roadtrip(self):
        response = self.client.post(
            '/api/roadtrips', json=self.payload,
            content_type='application/json'
        )
        self.assertEqual(401, response.status_code)

        data = json.loads(response.data.decode('utf-8'))
        assert_payload_field_type_value(
            self, data, 'error', int, 401
        )
        assert_payload_field_type_value(
            self, data, 'message', str, 'unauthorized'
        )
        assert_payload_field_type_value(
            self, data, 'success', bool, False
        )


# noinspection DuplicatedCode
class ManagerUserTest(CreateRoadtripTest):
    @patch('api.auth.auth.verify_decode_jwt')
    @patch('api.auth.auth.get_token_auth_header')
    def test_endpoint_happypath_create_roadtrip(
            self, mock_get_token_auth_header, mock_verify_decode_jwt):
        mock_get_token_auth_header.return_value = 'tripper-token'
        mock_verify_decode_jwt.return_value = {
            'permissions': ['get:roadtrips', 'create:roadtrips',
                            'update:roadtrips', 'delete:roadtrips']
        }

        payload = deepcopy(self.payload)
        response = self.client.post(
            '/api/roadtrips', json=payload,
            content_type='application/json'
        )
        self.assertEqual(201, response.status_code)

        data = json.loads(response.data.decode('utf-8'))
        assert_payload_field_type_value(self, data, 'success', bool, True)

        assert_payload_field_type(self, data, 'id', int)
        roadtrip_id = data['id']
        assert_payload_field_type_value(
            self, data, 'name', str, payload['name']
        )
        assert_payload_field_type_value(
            self, data, 'start_city', str, payload['start_city']
        )
        assert_payload_field_type_value(
            self, data, 'end_city', str, payload['end_city']
        )

        assert_payload_field_type(self, data, 'links', dict)
        links = data['links']
        assert_payload_field_type_value(
            self, links, 'get', str, f'/api/roadtrips/{roadtrip_id}'
        )
        assert_payload_field_type_value(
            self, links, 'patch', str, f'/api/roadtrips/{roadtrip_id}'
        )
        assert_payload_field_type_value(
            self, links, 'delete', str, f'/api/roadtrips/{roadtrip_id}'
        )
        assert_payload_field_type_value(
            self, links, 'index', str, '/api/roadtrips'
        )

