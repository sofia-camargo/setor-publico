import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from gafia_docs import Handler


class ServerSmokeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Handler.index = object()
        Handler.token = "test-token"
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def test_interface_assets_are_served(self):
        for path in ("/", "/style.css", "/app.js"):
            with self.subTest(path=path), urlopen(self.base + path) as response:
                self.assertEqual(response.status, 200)
                self.assertTrue(response.read())

    def test_token_is_required_for_status_and_chat(self):
        for path in ("/api/status", "/api/chat"):
            request = Request(self.base + path, method="POST" if path.endswith("chat") else "GET")
            with self.subTest(path=path):
                with self.assertRaises(HTTPError) as result:
                    urlopen(request)
                self.assertEqual(result.exception.code, 401)

    def test_status_reports_missing_index(self):
        request = Request(self.base + "/api/status", headers={"Authorization": "Bearer test-token"})
        with urlopen(request) as response:
            result = json.load(response)
        self.assertFalse(result["pronto"])
        self.assertIn("index", result["mensagem"])


if __name__ == "__main__":
    unittest.main()
