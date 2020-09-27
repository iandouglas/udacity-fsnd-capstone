import unittest
from sqlalchemy.exc import IntegrityError

from api import create_app, db
from api.database.models import User


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

    def test_user_model(self):
        user = User(username='ian')
        user.insert()

        self.assertIsInstance(user, User)
        self.assertIsNotNone(user.id)
        self.assertEqual('ian', user.username)

    def test_user_model_trimmed_username(self):
        user = User(username=' ian ')
        user.insert()

        self.assertIsInstance(user, User)
        self.assertIsNotNone(user.id)
        self.assertEqual('ian', user.username)

    def test_user_model_unique_username(self):
        user = User(username='ian')
        user.insert()

        try:
            user = User(username='ian')
            user.insert()
        except IntegrityError:
            self.assertTrue(True)
        else:
            # we should not end up in here
            self.assertTrue(False)  # pragma: no cover

    def test_user_model_blank_username(self):
        try:
            user = User(username='')
            user.insert()
        except IntegrityError:
            self.assertTrue(True)
        else:
            # we should not end up in here
            self.assertTrue(False)  # pragma: no cover
