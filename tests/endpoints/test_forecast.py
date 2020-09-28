import json
import unittest

from api import create_app, db
from tests import db_drop_everything, assert_payload_field_type_value, \
    assert_payload_field_type


class ForecastTest(unittest.TestCase):
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

    def test_forecast_happypath(self):
        response = self.client.get('/api/forecast?location=Arvada,CO')
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(200, response.status_code)
        assert_payload_field_type_value(self, data, 'success', bool, True)

        assert_payload_field_type_value(
            self, data, 'location', str, 'Arvada, CO'
        )

        assert_payload_field_type(self, data, 'current_temp', str)
        self.assertEqual('F', data['current_temp'][-1])

        assert_payload_field_type(self, data, 'conditions', str)
        self.assertGreater(len(data['conditions']), 0)

    def test_forecast_sadpath(self):
        response = self.client.get('/api/forecast?location=lkajslkjsdf')
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(500, response.status_code)
        assert_payload_field_type_value(
            self, data, 'message', str, 'Server has encountered an '
                                        'unknown error'
        )
