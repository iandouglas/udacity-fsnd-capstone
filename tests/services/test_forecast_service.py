import unittest
from api import create_app, db
from api.services.forecast import ForecastService
from tests import assert_payload_field_type_value, assert_payload_field_type


class ForecastServiceTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.latlng = {
            'success': True,
            'lat': 39.801122,
            'lng': -105.081451,
        }

        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_get_forecast_happypath(self):
        forecast = ForecastService.get_forecast(self.latlng)
        assert_payload_field_type_value(self, forecast, 'success', bool, True)
        assert_payload_field_type(self, forecast, 'current_temp', str)
        self.assertEqual('F', forecast['current_temp'][-1])
        assert_payload_field_type(self, forecast, 'conditions', str)
        self.assertGreater(len(forecast['conditions']), 0)

    def test_get_forecast_sadpath(self):
        sad_payload = {
            'success': False
        }
        forecast = ForecastService.get_forecast(sad_payload)
        assert_payload_field_type_value(self, forecast, 'success', bool, False)
        assert_payload_field_type_value(self, forecast, 'current_temp', str, '')
        assert_payload_field_type_value(self, forecast, 'conditions', str, '')
