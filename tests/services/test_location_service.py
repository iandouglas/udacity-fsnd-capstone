import unittest
from api import create_app, db
from api.database.models import City
from api.services.location import LocationService
from tests import assert_payload_field_type_value, assert_payload_field_type


class LocationServiceTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_get_latlng_happypath_with_dblookup(self):
        city = City(
            name='Arvada', state='CO',
            lat=1.23, lng=3.45,
            city_id=1
        )
        city.insert()

        latlng = LocationService.get_latlng('Arvada', 'CO')
        assert_payload_field_type_value(self, latlng, 'success', bool, True)
        assert_payload_field_type_value(self, latlng, 'lat', float, 1.23)
        assert_payload_field_type_value(self, latlng, 'lng', float, 3.45)
        assert_payload_field_type(self, latlng, 'id', int)
        self.assertGreater(latlng['id'], 0)

    def test_get_latlng_happypath_with_apilookup(self):
        latlng = LocationService.get_latlng('Ottawa', 'ON')
        assert_payload_field_type_value(self, latlng, 'success', bool, True)
        assert_payload_field_type_value(self, latlng, 'lat', float, 45.420421)
        assert_payload_field_type_value(self, latlng, 'lng', float, -75.692432)
        self.assertGreater(latlng['id'], 0)

    def test_get_latlng_sadpath_blank_city(self):
        latlng = LocationService.get_latlng('', 'CO')
        assert_payload_field_type_value(self, latlng, 'success', bool, False)
        assert_payload_field_type_value(self, latlng, 'lat', float, -90)
        assert_payload_field_type_value(self, latlng, 'lng', float, -180)
        assert_payload_field_type_value(
            self, latlng, 'error', str, 'city is required'
        )

    def test_get_latlng_sadpath_missing_city(self):
        latlng = LocationService.get_latlng(city=None, state='CO')
        assert_payload_field_type_value(self, latlng, 'success', bool, False)
        assert_payload_field_type_value(self, latlng, 'lat', float, -90)
        assert_payload_field_type_value(self, latlng, 'lng', float, -180)
        assert_payload_field_type_value(
            self, latlng, 'error', str, 'city is required'
        )

    def test_get_latlng_sadpath_blank_state(self):
        latlng = LocationService.get_latlng('Arvada', '')
        assert_payload_field_type_value(self, latlng, 'success', bool, False)
        assert_payload_field_type_value(self, latlng, 'lat', float, -90)
        assert_payload_field_type_value(self, latlng, 'lng', float, -180)
        assert_payload_field_type_value(
            self, latlng, 'error', str, 'state is required'
        )

    def test_get_latlng_sadpath_missing_state(self):
        latlng = LocationService.get_latlng(city='Arvada', state=None)
        assert_payload_field_type_value(self, latlng, 'success', bool, False)
        assert_payload_field_type_value(self, latlng, 'lat', float, -90)
        assert_payload_field_type_value(self, latlng, 'lng', float, -180)
        assert_payload_field_type_value(
            self, latlng, 'error', str, 'state is required'
        )

