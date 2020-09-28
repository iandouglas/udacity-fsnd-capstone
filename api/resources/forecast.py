from flask_restful import Resource, reqparse


class ForecastResource(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('location', type=str, help='Location is required')
        args = parser.parse_args()
        city, state = [x.strip() for x in args['location'].split(',')]
        return {
            'success': True,
            'location': f'{city}, {state}',
            'current_temp': '0',
            'conditions': '',
        }
