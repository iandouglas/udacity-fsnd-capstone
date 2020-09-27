import unittest

from api import create_app, db
from api.database.models import User
from tests import seed_data, db_drop_everything


class AppTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        seed_data(db)
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db_drop_everything(db)
        self.app_context.pop()

    def test_user_model(self):
        user = User(username='ian')

        self.assertIs(user, User)
        self.assertEqual('ian', user.username)
