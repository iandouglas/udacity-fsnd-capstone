from flask_restful import Resource, reqparse

from api.services.forecast import ForecastService
from api.services.location import LocationService


class ForecastResource(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('location', type=str, help='Location is required')
        args = parser.parse_args()
        city, state = [x.strip() for x in args['location'].split(',')]

        latlng = LocationService.get_latlng(city, state)
        if latlng['success']:

            forecast = ForecastService.get_forecast(latlng)
            if forecast['success']:
                return {
                    'success': True,
                    'location': f'{city}, {state}',
                    'current_temp': forecast['current_temp'],
                    'conditions': forecast['conditions'],
                }

        return {
            'success': False,
            'location': f'{city}, {state}',
            'current_temp': '',
            'conditions': '',
        }
