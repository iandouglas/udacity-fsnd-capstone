import json
import unittest
from copy import deepcopy
from unittest.mock import patch

from api import create_app, db
from api.database.models import RoadTrip
from api.services.location import LocationService
from tests import db_drop_everything, assert_payload_field_type_value, \
    assert_payload_field_type


class PatchRoadtripTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

        self.arvada = LocationService.get_latlng('Arvada', 'CO')
        self.denver = LocationService.get_latlng('Denver', 'CO')

        self.roadtrip_1 = RoadTrip(
            name='commute to work',
            start_city_id=self.arvada['id'],
            end_city_id=self.denver['id'],
        )
        self.roadtrip_1.insert()

        self.payload = {
            'name': ' commute home ',
            'start_city': ' Denver, CO ',
            'end_city': ' Arvada, CO ',
        }

    def tearDown(self):
        db.session.remove()
        db_drop_everything(db)
        self.app_context.pop()


class GuestUserTest(PatchRoadtripTest):
    def test_endpoint_badauth_get_a_roadtrip(self):
        response = self.client.patch(
            f'/api/roadtrips/{self.roadtrip_1.id}',
            json=self.payload,
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
class UserTest(PatchRoadtripTest):
    @patch('api.auth.auth.verify_decode_jwt')
    @patch('api.auth.auth.get_token_auth_header')
    def test_endpoint_happypath_patch_a_roadtrip(
            self, mock_get_token_auth_header, mock_verify_decode_jwt):
        mock_get_token_auth_header.return_value = 'tripper-token'
        mock_verify_decode_jwt.return_value = {
            'permissions': ['get:roadtrips', 'create:roadtrips',
                            'update:roadtrips', 'delete:roadtrips']
        }

        payload = deepcopy(self.payload)
        response = self.client.patch(
            f'/api/roadtrips/{self.roadtrip_1.id}',
            json=payload,
            content_type='application/json'
        )
        self.assertEqual(200, response.status_code)

        data = json.loads(response.data.decode('utf-8'))
        assert_payload_field_type_value(self, data, 'success', bool, True)

        assert_payload_field_type_value(
            self, data, 'name', str, payload['name'].strip()
        )
        assert_payload_field_type_value(
            self, data, 'start_city', str,
            payload['start_city'].strip()
        )
        assert_payload_field_type_value(
            self, data, 'end_city', str,
            payload['end_city'].strip()
        )

    @patch('api.auth.auth.verify_decode_jwt')
    @patch('api.auth.auth.get_token_auth_header')
    def test_endpoint_sadpath_patch_blank_name(
            self, mock_get_token_auth_header, mock_verify_decode_jwt):
        mock_get_token_auth_header.return_value = 'tripper-token'
        mock_verify_decode_jwt.return_value = {
            'permissions': ['get:roadtrips', 'create:roadtrips',
                            'update:roadtrips', 'delete:roadtrips']
        }

        payload = deepcopy(self.payload)
        payload['name'] = ''
        response = self.client.patch(
            f'/api/roadtrips/{self.roadtrip_1.id}',
            json=payload,
            content_type='application/json'
        )
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(400, response.status_code)
        assert_payload_field_type_value(self, data, 'success', bool, False)
        assert_payload_field_type_value(self, data, 'error', int, 400)
        assert_payload_field_type_value(
            self, data, 'errors', list, ["required 'name' parameter is blank"]
        )

    @patch('api.auth.auth.verify_decode_jwt')
    @patch('api.auth.auth.get_token_auth_header')
    def test_endpoint_sadpath_patch_blank_start_city(
            self, mock_get_token_auth_header, mock_verify_decode_jwt):
        mock_get_token_auth_header.return_value = 'tripper-token'
        mock_verify_decode_jwt.return_value = {
            'permissions': ['get:roadtrips', 'create:roadtrips',
                            'update:roadtrips', 'delete:roadtrips']
        }

        payload = deepcopy(self.payload)
        payload['start_city'] = ''
        response = self.client.patch(
            f'/api/roadtrips/{self.roadtrip_1.id}',
            json=payload,
            content_type='application/json'
        )
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(400, response.status_code)
        assert_payload_field_type_value(self, data, 'success', bool, False)
        assert_payload_field_type_value(self, data, 'error', int, 400)
        assert_payload_field_type_value(
            self, data, 'errors', list,
            ["required 'start_city' parameter is blank"]
        )

    @patch('api.auth.auth.verify_decode_jwt')
    @patch('api.auth.auth.get_token_auth_header')
    def test_endpoint_sadpath_patch_blank_end_city(
            self, mock_get_token_auth_header, mock_verify_decode_jwt):
        mock_get_token_auth_header.return_value = 'tripper-token'
        mock_verify_decode_jwt.return_value = {
            'permissions': ['get:roadtrips', 'create:roadtrips',
                            'update:roadtrips', 'delete:roadtrips']
        }

        payload = deepcopy(self.payload)
        payload['end_city'] = ''
        response = self.client.patch(
            f'/api/roadtrips/{self.roadtrip_1.id}',
            json=payload,
            content_type='application/json'
        )
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(400, response.status_code)
        assert_payload_field_type_value(self, data, 'success', bool, False)
        assert_payload_field_type_value(self, data, 'error', int, 400)
        assert_payload_field_type_value(
            self, data, 'errors', list,
            ["required 'end_city' parameter is blank"]
        )

    @patch('api.auth.auth.verify_decode_jwt')
    @patch('api.auth.auth.get_token_auth_header')
    def test_endpoint_sadpath_patch_roadtrip_bad_id(
            self, mock_get_token_auth_header, mock_verify_decode_jwt):
        mock_get_token_auth_header.return_value = 'tripper-token'
        mock_verify_decode_jwt.return_value = {
            'permissions': ['get:roadtrips', 'create:roadtrips',
                            'update:roadtrips', 'delete:roadtrips']
        }

        response = self.client.patch(
            f'/api/roadtrips/9999'
        )
        self.assertEqual(404, response.status_code)

        data = json.loads(response.data.decode('utf-8'))
        assert_payload_field_type_value(self, data, 'error', int, 404)
        assert_payload_field_type_value(self, data, 'success', bool, False)
        assert_payload_field_type_value(
            self, data, 'message', str, 'resource not found'
        )
