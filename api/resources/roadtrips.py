import datetime
import json

import bleach
from flask import request
from flask_restful import Resource, abort
from sqlalchemy.orm.exc import NoResultFound

from api import requires_auth, db
from api.database.models import RoadTrip
from api.services.forecast import ForecastService
from api.services.location import LocationService


def _validate_name(data, field, proceed, errors, missing_okay=False):
    if field in data:
        data[field] = bleach.clean(data[field].strip())
        if len(data[field]) == 0:
            proceed = False
            errors.append(f"required '{field}' parameter is blank")
    if not missing_okay and field not in data:
        proceed = False
        errors.append(f"required '{field}' parameter is missing")
        data[field] = ''

    return proceed, data[field], errors


def _validate_city(data, field, proceed, errors, missing_okay=False):
    city_payload = {}
    if not missing_okay and field not in data:
        proceed = False
        errors.append(f"required '{field}' parameter is missing")
    else:
        data[field] = bleach.clean(data[field].strip())
        if len(data[field]) == 0:
            proceed = False
            errors.append(f"required '{field}' parameter is blank")
        else:
            city, state = [x.strip() for x in data[field].split(',')]
            city_payload = LocationService.get_latlng(city, state)
    return proceed, city_payload, errors


class RoadtripsResource(Resource):
    method_decorators = {
        'post': [requires_auth('create:roadtrips')],
        'get': [requires_auth('get:roadtrips')]
    }

    def _create_trip(self, data):
        proceed = True
        errors = []

        proceed, trip_name, errors = _validate_name(
            data, 'name', proceed, errors)
        if trip_name:
            data['name'] = trip_name
        proceed, city_1, errors = _validate_city(
            data, 'start_city', proceed, errors)
        proceed, city_2, errors = _validate_city(
            data, 'end_city', proceed, errors)

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
                'start_city': roadtrip.start_city().city_state(),
                'end_city': roadtrip.end_city().city_state(),
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
                'error': 400,
                'errors': errors
            }, 400

    def get(self, *args, **kwargs):
        trips = RoadTrip.query.order_by(
            RoadTrip.name.asc()
        ).all()
        results = [{
            'name': rt.name,
            'start_city': rt.start_city().city_state(),
            'end_city': rt.end_city().city_state(),
            'travel_time': LocationService.route_distance_time(
                rt.start_city(), rt.end_city())['string']
            } for rt in trips]
        return {
            'success': True,
            'results': results
        }, 200


class RoadtripResource(Resource):
    method_decorators = {
        'get': [requires_auth('get:roadtrips')],
        'delete': [requires_auth('delete:roadtrips')],
        'patch': [requires_auth('update:roadtrips')]
    }

    def get(self, *args, **kwargs):
        roadtrip_id = int(bleach.clean(kwargs['roadtrip_id'].strip()))
        rt = None
        try:
            rt = db.session.query(RoadTrip).filter_by(id=roadtrip_id).one()
        except NoResultFound:
            return abort(404)

        sc = rt.start_city()
        ec = rt.end_city()

        travel_time = LocationService.route_distance_time(sc, ec)
        forecast = ForecastService.get_forecast(
            {'success': True, 'lat': ec.lat, 'lng': ec.lng}, hourly=True
        )
        hrs = max(round(travel_time['seconds']//3600) - 1, 0)
        forecast = forecast['hourly'][hrs]
        return {
            'success': True,
            'name': rt.name,
            'start_city': sc.city_state(),
            'end_city': ec.city_state(),
            'travel_time': travel_time['string'],
            'forecast_at_eta': {
                'temp': f'{forecast["temp"]}F',
                'conditions': forecast['weather'][0]['description']
            }
        }, 200

    def patch(self, *args, **kwargs):
        roadtrip_id = int(bleach.clean(kwargs['roadtrip_id'].strip()))
        rt = None
        try:
            rt = db.session.query(RoadTrip).filter_by(id=roadtrip_id).one()
        except NoResultFound:
            return abort(404)

        proceed = True
        errors = []
        data = json.loads(request.data)
        proceed, trip_name, errors = _validate_name(
            data, 'name', proceed, errors, missing_okay=True)
        proceed, start_city, errors = _validate_city(
            data, 'start_city', proceed, errors, missing_okay=True)
        proceed, end_city, errors = _validate_city(
            data, 'end_city', proceed, errors, missing_okay=True)
        if not proceed:
            return {
                'success': False,
                'error': 400,
                'errors': errors
            }, 400

        if trip_name and len(trip_name.strip()) > 0:
            rt.name = trip_name
        if start_city:
            rt.start_city_id = start_city['id']
        if end_city:
            rt.end_city_id = end_city['id']
        rt.update()

        return {
            'success': True,
            'name': rt.name,
            'start_city': rt.start_city().city_state(),
            'end_city': rt.end_city().city_state(),
        }, 200

    def delete(self, *args, **kwargs):
        roadtrip_id = kwargs['roadtrip_id']
        rt = None
        try:
            rt = db.session.query(RoadTrip).filter_by(id=roadtrip_id).one()
        except NoResultFound:
            return abort(404)

        rt.delete()
        return {}, 204
