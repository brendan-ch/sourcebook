from test.test_app import TestFlaskApp


class TestIndexBlueprint(TestFlaskApp):
    def test_all_classes(self):
        response = self.app.get("/")
        self.assertEqual(response.status_code, 200)