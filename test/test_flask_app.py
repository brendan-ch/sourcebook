import unittest

from app import create_app
from test.test_with_database_container import TestWithDatabaseContainer


class TestFlaskApp(TestWithDatabaseContainer):
    def setUp(self):
        super().setUp()
        self.app = create_app()
        self.test_client = self.app.test_client()
        self.test_client.testing = True
