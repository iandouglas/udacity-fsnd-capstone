import bleach
from sqlalchemy import Column, String, Integer, Float
import json
from api import db


class EmptyClass(object):
    pass


class User(db.Model):
    """
    User Model
    """
    __tablename__ = 'users'

    # Auto-incrementing, unique primary key
    id = Column(Integer, primary_key=True)
    # unique username
    username = Column(String(80), unique=True, nullable=False)
    # unique email
    email = Column(String(100), unique=True, nullable=False)

    def __init__(self, username, email, user_id=None):
        if username is not None:
            username = bleach.clean(username).strip()
            if username == '':
                username = None

        if email is not None:
            email = bleach.clean(email).strip()
            if email == '':
                email = None

        self.username = username
        self.email = email
        if user_id is not None:
            self.id = user_id

    def insert(self):
        """
        inserts a new model into a database
        the model must have a unique username
        the model must have a unique id or null id
        """
        db.session.add(self)
        db.session.commit()


class City(db.Model):
    """
    City Model
    """
    __tablename__ = 'cities'

    # Auto-incrementing, unique primary key
    id = Column(Integer, primary_key=True)
    # unique username
    name = Column(String(80), nullable=False)
    state = Column(String(2), nullable=False)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)

    def __init__(self, name, state, lat, lng, city_id=None):
        if name is not None:
            name = name.strip()
            if name == '':
                name = None
        if state is not None:
            state = state.strip()
            if state == '':
                state = None

        self.name = name
        self.state = state
        self.lat = lat
        self.lng = lng
        if city_id is not None:
            self.id = city_id

    def insert(self):
        """
        inserts a new model into a database
        the model must have a unique username
        the model must have a unique id or null id
        """
        db.session.add(self)
        db.session.commit()


class RoadTrip(db.Model):
    """
    RoadTrip Model
    """
    __tablename__ = 'roadtrips'

    # Auto-incrementing, unique primary key
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    start_city_id = db.Column(
        db.Integer,
        db.ForeignKey('cities.id'),
        nullable=False
    )
    end_city_id = db.Column(
        db.Integer,
        db.ForeignKey('cities.id'),
        nullable=False
    )

    def __init__(self, name, start_city_id, end_city_id):
        if name is not None:
            name = name.strip()
            if name == '':
                name = None

        self.name = name
        self.start_city_id = start_city_id
        self.end_city_id = end_city_id

    def start_city(self):
        chk = db.session.query(City).get(self.start_city_id)
        if chk:
            return f'{chk.name}, {chk.state}'

    def end_city(self):
        chk = db.session.query(City).get(self.end_city_id)
        if chk:
            return f'{chk.name}, {chk.state}'

    def insert(self):
        """
        inserts a new model into a database
        the model must have a unique username
        the model must have a unique id or null id
        """
        db.session.add(self)
        db.session.commit()
