import json, tempfile, unittest
from pathlib import Path
from scripts.generate_caption import _parse_caption, _safe_stem, generate_caption

class CaptionGenerationTests(unittest.TestCase):
    def test_safe_stem_rejects_paths(self):
        with self.assertRaisesRegex(ValueError, "filename"):
            _safe_stem("../alicia.png")
    def test_safe_stem_rejects_non_png(self):
        with self.assertRaisesRegex(ValueError, "Only PNG"):
            _safe_stem("alicia.jpg")
    def test_parse_json_caption_and_hashtags(self):
        caption, hashtags = _parse_caption('{"caption":"A slow afternoon ☕","hashtags":["Alicia","citylife","citylife"]}')
        self.assertEqual(caption, "A slow afternoon ☕")
        self.assertEqual(hashtags, ["#Alicia", "#citylife"])
    def test_parse_plain_text_response(self):
        caption, hashtags = _parse_caption("A quiet moment between plans.")
        self.assertEqual(caption, "A quiet moment between plans.")
        self.assertEqual(hashtags, [])
    def test_generate_caption_writes_draft_without_publishing(self):
        class FakeResponse:
            status_code = 200
            text = ""
            def json(self):
                return {"result":{"response":'{"caption":"A little pause in the day.","hashtags":["dailyvibes","citylife"]}'}}
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); selected = root / "selected"; captions = root / "captions"; selected.mkdir()
            (selected / "alicia.png").write_bytes(b"placeholder")
            calls = []
            def fake_post(*args, **kwargs):
                calls.append((args, kwargs)); return FakeResponse()
            destination, record = generate_caption("alicia.png", selected, captions, "token", "account", fake_post)
            self.assertTrue(destination.is_file())
            self.assertEqual(record["status"], "draft_not_published")
            self.assertEqual(json.loads(destination.read_text())["caption"], "A little pause in the day.")
            self.assertEqual(len(calls), 1)
    def test_refuses_to_overwrite_existing_caption(self):
        class FakeResponse:
            status_code = 200
            text = ""
            def json(self):
                return {"result":{"response":'{"caption":"A day out.","hashtags":["daily"]}'}}
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); selected = root / "selected"; captions = root / "captions"
            selected.mkdir(); captions.mkdir(); (selected / "alicia.png").write_bytes(b"x")
            (captions / "alicia.json").write_text("keep", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                generate_caption("alicia.png", selected, captions, "token", "account", lambda *a, **k: FakeResponse())
            self.assertEqual((captions / "alicia.json").read_text(), "keep")

if __name__ == "__main__":
    unittest.main()
