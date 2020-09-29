import json
import unittest
from copy import deepcopy
from unittest.mock import patch

from api import create_app, db
from api.database.models import RoadTrip
from api.services.location import LocationService
from tests import db_drop_everything, assert_payload_field_type_value, \
    assert_payload_field_type


class GetCitiesTest(unittest.TestCase):
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


class GuestUserTest(GetCitiesTest):
    def test_endpoint_badauth_get_all_roadtrips(self):
        response = self.client.get(
            f'/api/roadtrips'
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
class UserTest(GetCitiesTest):
    @patch('api.auth.auth.verify_decode_jwt')
    @patch('api.auth.auth.get_token_auth_header')
    def test_endpoint_happypath_get_all_cities(
            self, mock_get_token_auth_header, mock_verify_decode_jwt):
        mock_get_token_auth_header.return_value = 'tripper-token'
        mock_verify_decode_jwt.return_value = {
            'permissions': ['get:roadtrips', 'create:roadtrips',
                            'update:roadtrips', 'delete:roadtrips']
        }

        arvada = LocationService.get_latlng('Arvada', 'CO')
        denver = LocationService.get_latlng('Denver', 'CO')
        estes = LocationService.get_latlng('Estes Park', 'CO')

        RoadTrip(
            name='rt1',
            start_city_id=arvada['id'],
            end_city_id=denver['id'],
        ).insert()

        RoadTrip(
            name='rt2',
            start_city_id=arvada['id'],
            end_city_id=estes['id'],
        ).insert()

        RoadTrip(
            name='rt3',
            start_city_id=denver['id'],
            end_city_id=arvada['id'],
        ).insert()

        RoadTrip(
            name='rt4',
            start_city_id=denver['id'],
            end_city_id=estes['id'],
        ).insert()

        response = self.client.get(
            f'/api/cities'
        )
        self.assertEqual(200, response.status_code)

        data = json.loads(response.data.decode('utf-8'))
        assert_payload_field_type_value(self, data, 'success', bool, True)

        assert_payload_field_type(self, data, 'starting_cities', dict)
        self.assertEqual(2, len(data['starting_cities']))
        cities = data['starting_cities']
        assert_payload_field_type_value(self, cities, 'Arvada, CO', int, 2)
        assert_payload_field_type_value(self, cities, 'Denver, CO', int, 2)

        assert_payload_field_type(self, data, 'ending_cities', dict)
        self.assertEqual(3, len(data['ending_cities']))
        cities = data['ending_cities']
        assert_payload_field_type_value(self, cities, 'Arvada, CO', int, 1)
        assert_payload_field_type_value(self, cities, 'Denver, CO', int, 1)
        assert_payload_field_type_value(self, cities, 'Estes Park, CO', int, 2)

    @patch('api.auth.auth.verify_decode_jwt')
    @patch('api.auth.auth.get_token_auth_header')
    def test_endpoint_happypath_get_no_cities(
            self, mock_get_token_auth_header, mock_verify_decode_jwt):
        mock_get_token_auth_header.return_value = 'tripper-token'
        mock_verify_decode_jwt.return_value = {
            'permissions': ['get:roadtrips', 'create:roadtrips',
                            'update:roadtrips', 'delete:roadtrips']
        }

        response = self.client.get(
            f'/api/cities'
        )
        self.assertEqual(200, response.status_code)

        data = json.loads(response.data.decode('utf-8'))
        assert_payload_field_type_value(self, data, 'success', bool, True)

        assert_payload_field_type(self, data, 'starting_cities', dict)
        self.assertEqual(0, len(data['starting_cities']))

        assert_payload_field_type(self, data, 'ending_cities', dict)
        self.assertEqual(0, len(data['ending_cities']))

