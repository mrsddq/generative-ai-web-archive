"""HTTP contract tests; no Azure credentials or paid calls are used."""
import importlib.util
from pathlib import Path
import unittest
import sys
from unittest.mock import patch, Mock
import requests

spec = importlib.util.spec_from_file_location("translator", Path(__file__).resolve().parents[1] / "AI-Web-App/app.py")
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class TranslatorTests(unittest.TestCase):
    def setUp(self):
        self.client = module.app.test_client()
        self.env = patch.dict("os.environ", {"KEY": "test-key", "ENDPOINT": "https://translator.example", "LOCATION": "test-region"})
        self.env.start()
        self.addCleanup(self.env.stop)

    def test_form_renders(self):
        self.assertEqual(self.client.get("/").status_code, 200)

    @patch.object(module.requests, "post")
    def test_translation_and_request_contract(self, post):
        post.return_value = Mock(json=lambda: [{"translations": [{"text": "Hola"}]}])
        response = self.client.post("/", data={"text": "Hello", "language": "es"})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Hola", response.data)
        self.assertEqual(post.call_args.kwargs["params"], {"api-version": "3.0", "to": "es"})
        self.assertEqual(post.call_args.kwargs["timeout"], 20)
        self.assertEqual(post.call_args.kwargs["json"], [{"text": "Hello"}])

    @patch.object(module.requests, "post")
    def test_bad_input_never_calls_service(self, post):
        for data in ({"text": " "}, {"text": "x" * 5001}, {"text": "Hello", "language": "es&to=fr"}):
            with self.subTest(data_size=len(data["text"])):
                self.assertEqual(self.client.post("/", data=data).status_code, 400)
        post.assert_not_called()

    @patch.object(module.requests, "post")
    def test_upstream_failure_does_not_disclose_details(self, post):
        post.side_effect = requests.Timeout("sensitive provider detail")
        response = self.client.post("/", data={"text": "Hello"})
        self.assertEqual(response.status_code, 502)
        self.assertNotIn(b"sensitive provider detail", response.data)

    @patch.object(module.requests, "post", side_effect=requests.Timeout)
    def test_errors_preserve_form_input_as_escaped_text(self, post):
        for text, status in ((" <script>alert(1)</script> ", 502), ("x" * 5001, 400)):
            with self.subTest(status=status):
                response = self.client.post("/", data={"text": text, "language": "de"})
                self.assertEqual(response.status_code, status)
                escaped = text.replace("<", "&lt;").replace(">", "&gt;").encode()
                self.assertIn(escaped + b"</textarea>", response.data)
                self.assertIn(b'<option value="de" selected>', response.data)
                self.assertNotIn(b"<script>", response.data)

    @patch.object(module.requests, "post")
    def test_malformed_responses_are_handled(self, post):
        for payload in ([], None, {}, [{"translations": []}], [{"translations": [{"text": 42}]}]):
            post.return_value = Mock(json=lambda: payload)
            with self.subTest(payload=payload):
                self.assertEqual(self.client.post("/", data={"text": "Hello"}).status_code, 502)

    @patch.object(module.requests, "post")
    def test_missing_configuration_is_handled(self, post):
        with patch.dict("os.environ", {}, clear=True):
            self.assertEqual(self.client.post("/", data={"text": "Hello"}).status_code, 502)
        post.assert_not_called()


if __name__ == "__main__":
    unittest.main()
