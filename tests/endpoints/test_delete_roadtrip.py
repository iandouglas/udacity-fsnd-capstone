import json
import unittest
from unittest.mock import patch

from api import create_app, db
from api.database.models import RoadTrip
from api.services.location import LocationService
from tests import db_drop_everything, assert_payload_field_type_value, \
    assert_payload_field_type


class GetRoadtripTest(unittest.TestCase):
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

    def tearDown(self):
        db.session.remove()
        db_drop_everything(db)
        self.app_context.pop()


class GuestUserTest(GetRoadtripTest):
    def test_endpoint_badauth_delete_a_roadtrip(self):
        response = self.client.delete(
            f'/api/roadtrips/{self.roadtrip_1.id}'
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
class UserTest(GetRoadtripTest):
    @patch('api.auth.auth.verify_decode_jwt')
    @patch('api.auth.auth.get_token_auth_header')
    def test_endpoint_happypath_delete_a_roadtrip(
            self, mock_get_token_auth_header, mock_verify_decode_jwt):
        mock_get_token_auth_header.return_value = 'tripper-token'
        mock_verify_decode_jwt.return_value = {
            'permissions': ['get:roadtrips', 'create:roadtrips',
                            'update:roadtrips', 'delete:roadtrips']
        }

        response = self.client.delete(
            f'/api/roadtrips/{self.roadtrip_1.id}'
        )
        self.assertEqual(204, response.status_code)
        self.assertEqual('', response.data.decode('utf-8'))

        response = self.client.get(
            f'/api/roadtrips/{self.roadtrip_1.id}'
        )
        self.assertEqual(404, response.status_code)


    @patch('api.auth.auth.verify_decode_jwt')
    @patch('api.auth.auth.get_token_auth_header')
    def test_endpoint_sadpath_delete_bad_id_roadtrip(
            self, mock_get_token_auth_header, mock_verify_decode_jwt):
        mock_get_token_auth_header.return_value = 'tripper-token'
        mock_verify_decode_jwt.return_value = {
            'permissions': ['get:roadtrips', 'create:roadtrips',
                            'update:roadtrips', 'delete:roadtrips']
        }

        response = self.client.delete(
            f'/api/roadtrips/9999'
        )
        self.assertEqual(404, response.status_code)

        data = json.loads(response.data.decode('utf-8'))
        assert_payload_field_type_value(self, data, 'error', int, 404)
        assert_payload_field_type_value(self, data, 'success', bool, False)
        assert_payload_field_type_value(
            self, data, 'message', str, 'resource not found'
        )
