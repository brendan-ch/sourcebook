import unittest
import uuid
from typing import Optional

from app import create_app
from models.user import User
from test.test_with_database_container import TestWithDatabaseContainer


class TestFlaskApp(TestWithDatabaseContainer):
    def setUp(self):
        super().setUp()
        self.app = create_app(self.database_config)
        self.test_client = self.app.test_client()
        self.test_client.testing = True

    def sign_user_into_session(self, user: Optional[User] = None):
        if not user:
            uuid_to_set = str(uuid.uuid4())
        else:
            uuid_to_set = user.user_uuid

        with self.test_client.session_transaction() as session:
            session["user_uuid"] = uuid_to_set
