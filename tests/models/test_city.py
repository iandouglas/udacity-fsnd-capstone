import unittest
from sqlalchemy.exc import IntegrityError

from api import create_app, db
from api.database.models import City


class AppTest(unittest.TestCase):
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

    def test_city_model(self):
        city = City(name='Arvada', state='CO', lat=1.23, lng=3.45)
        city.insert()

        self.assertIsInstance(city, City)
        self.assertIsNotNone(city.id)
        self.assertEqual('Arvada', city.name)
        self.assertEqual('CO', city.state)
        self.assertEqual(1.23, city.lat)
        self.assertEqual(3.45, city.lng)

    def test_city_model_trimmed_strings(self):
        city = City(name=' Arvada ', state=' CO ', lat=1.23, lng=3.45)
        city.insert()

        self.assertEqual('Arvada', city.name)
        self.assertEqual('CO', city.state)

    def test_city_model_blank_city(self):
        try:
            city = City(name='', state='CO', lat=1.23, lng=3.45)
            city.insert()
        except IntegrityError:
            self.assertTrue(True)
        else:
            # we should not end up in here
            self.assertTrue(False)  # pragma: no cover

    def test_city_model_mssing_city(self):
        try:
            city = City(name=None, state='CO', lat=1.23, lng=3.45)
            city.insert()
        except IntegrityError:
            self.assertTrue(True)
        else:
            # we should not end up in here
            self.assertTrue(False)  # pragma: no cover

    def test_city_model_blank_state(self):
        try:
            city = City(name='Arvada', state='', lat=1.23, lng=3.45)
            city.insert()
        except IntegrityError:
            self.assertTrue(True)
        else:
            # we should not end up in here
            self.assertTrue(False)  # pragma: no cover

    def test_city_model_missing_state(self):
        try:
            city = City(name='Arvada', state=None, lat=1.23, lng=3.45)
            city.insert()
        except IntegrityError:
            self.assertTrue(True)
        else:
            # we should not end up in here
            self.assertTrue(False)  # pragma: no cover

    def test_city_model_missing_lat(self):
        try:
            city = City(name='Arvada', state='CO', lat=None, lng=3.45)
            city.insert()
        except IntegrityError:
            self.assertTrue(True)
        else:
            # we should not end up in here
            self.assertTrue(False)  # pragma: no cover

    def test_city_model_missing_lng(self):
        try:
            city = City(name='Arvada', state='CO', lat=1.23, lng=None)
            city.insert()
        except IntegrityError:
            self.assertTrue(True)
        else:
            # we should not end up in here
            self.assertTrue(False)  # pragma: no cover
