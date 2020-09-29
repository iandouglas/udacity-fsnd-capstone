import datetime
import json

import bleach
from flask import request
from flask_restful import Resource, abort
from sqlalchemy import func
from sqlalchemy.orm.exc import NoResultFound

from api import requires_auth, db
from api.database.models import City, RoadTrip


class CitiesResource(Resource):
    method_decorators = {
        'get': [requires_auth('get:roadtrips')]
    }

    def get(self, *args, **kwargs):
        sc_list = db.session.query(City, func.count(RoadTrip.id)).\
            join(RoadTrip, RoadTrip.start_city_id==City.id).\
            group_by(City)
        starting_cities = {
            x[0].city_state(): x[1] for x in sc_list
        }
        ec_list = db.session.query(City, func.count(RoadTrip.id)).\
            join(RoadTrip, RoadTrip.end_city_id==City.id).\
            group_by(City)
        ending_cities = {
            x[0].city_state(): x[1] for x in ec_list
        }
        return {
            'success': True,
            'starting_cities': starting_cities,
            'ending_cities': ending_cities,
        }, 200
