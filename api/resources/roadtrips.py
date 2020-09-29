import json

import bleach
from flask import request
from flask_restful import Resource
from api import requires_auth, db
from api.database.models import RoadTrip
from api.services.location import LocationService


class RoadtripsResource(Resource):
    method_decorators = {
        'post': [requires_auth('create:roadtrips')]
    }

    def _create_trip(self, data):
        proceed = True
        errors = []
        city_1 = None
        city_2 = None

        if 'name' not in data:
            proceed = False
            errors.append("required 'name' parameter is missing")
        if 'name' in data:
            data['name'] = bleach.clean(data['name'].strip())
            if len(data['name']) == 0:
                proceed = False
                errors.append("required 'name' parameter is blank")

        if 'start_city' not in data:
            proceed = False
            errors.append("required 'start_city' parameter is missing")
        else:
            data['start_city'] = bleach.clean(data['start_city'].strip())
            if len(data['start_city']) == 0:
                proceed = False
                errors.append("required 'start_city' parameter is blank")
            else:
                city, state = [x.strip() for x in data['start_city'].split(',')]
                city_1 = LocationService.get_latlng(city, state)

        if 'end_city' not in data:
            proceed = False
            errors.append("required 'end_city' parameter is missing")
        else:
            data['end_city'] = bleach.clean(data['end_city'].strip())
            if len(data['end_city']) == 0:
                proceed = False
                errors.append("required 'end_city' parameter is blank")
            else:
                city, state = [x.strip() for x in data['end_city'].split(',')]
                city_2 = LocationService.get_latlng(city, state)

        if proceed:
            roadtrip = RoadTrip(
                name=data['name'],
                start_city_id=city_1['id'],
                end_city_id=city_2['id'],
            )
            db.session.add(roadtrip)
            db.session.commit()
            return roadtrip, errors
        else:
            return None, errors

    def post(self, *args, **kwargs):
        roadtrip, errors = self._create_trip(json.loads(request.data))
        if roadtrip is not None:
            return {
                'success': True,
                'id': roadtrip.id,
                'name': roadtrip.name,
                'start_city': roadtrip.start_city(),
                'end_city': roadtrip.end_city(),
                'links': {
                    'get': f'/api/roadtrips/{roadtrip.id}',
                    'patch': f'/api/roadtrips/{roadtrip.id}',
                    'delete': f'/api/roadtrips/{roadtrip.id}',
                    'index': '/api/roadtrips',
                }
            }, 201
        else:
            return {
                'success': False,
                'errors': errors
            }, 400

class RoadtripResource(Resource):
    method_decorators = {
        'get': [requires_auth('get:roadtrips')],
        'delete': [requires_auth('delete:roadtrips')],
        'patch': [requires_auth('patch:roadtrips')]
    }
    pass
