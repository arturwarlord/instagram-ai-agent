import unittest
from urllib.error import HTTPError

from scripts.check_instagram_connection import check_connection


class FakeResponse:
    status = 200

    def __init__(self, body):
        self.body = body.encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return self.body


class InstagramConnectionTests(unittest.TestCase):
    def test_reads_account_identity_without_publishing(self):
        calls = []

        def fake_open(request, timeout=20):
            calls.append((request, timeout))
            return FakeResponse('{"user_id":"12345","username":"alicia"}')

        result = check_connection("secret-token", opener=fake_open)
        self.assertEqual(result, {"user_id": "12345", "username": "alicia"})
        self.assertEqual(calls[0][0].method, "GET")
        self.assertIn("/me?", calls[0][0].full_url)
        self.assertNotIn("secret-token", repr(result))

    def test_requires_token(self):
        with self.assertRaisesRegex(ValueError, "Missing INSTAGRAM_ACCESS_TOKEN"):
            check_connection("")

    def test_rejects_invalid_api_version(self):
        with self.assertRaisesRegex(ValueError, "INSTAGRAM_API_VERSION"):
            check_connection("token", "latest", opener=lambda *a, **k: None)

    def test_does_not_expose_api_error_body(self):
        def fake_open(request, timeout=20):
            raise HTTPError(request.full_url, 400, "bad request", {}, None)

        with self.assertRaisesRegex(RuntimeError, "HTTP 400") as caught:
            check_connection("private-token", opener=fake_open)
        self.assertNotIn("private-token", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
