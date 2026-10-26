import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from scripts.prepare_post import _parse_bool, _parse_utc, prepare_post


class PreparePostTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.selected = root / "selected"
        self.captions = root / "captions"
        self.queue = root / "queue"
        self.selected.mkdir()
        self.captions.mkdir()
        self.now = datetime(2026, 10, 26, 12, 0, tzinfo=timezone.utc)
        (self.selected / "alicia.png").write_bytes(b"image")
        (self.captions / "alicia.json").write_text(json.dumps({
            "image": "alicia.png", "caption": "A quiet moment.",
            "hashtags": ["#Alicia"], "status": "draft_not_published",
        }), encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def test_parses_future_utc_timestamp(self):
        parsed = _parse_utc("2026-10-28T15:00:00Z", now=self.now)
        self.assertEqual(parsed.isoformat(), "2026-10-28T15:00:00+00:00")

    def test_rejects_timestamp_without_timezone(self):
        with self.assertRaisesRegex(ValueError, "include a timezone"):
            _parse_utc("2026-10-28T15:00:00", now=self.now)

    def test_rejects_non_utc_offset(self):
        with self.assertRaisesRegex(ValueError, "UTC time"):
            _parse_utc("2026-10-28T17:00:00+02:00", now=self.now)

    def test_rejects_past_time(self):
        with self.assertRaisesRegex(ValueError, "future"):
            _parse_utc("2026-10-25T15:00:00Z", now=self.now)

    def test_creates_unpublished_queue_entry_by_default(self):
        path, record = prepare_post("alicia.png", "2026-10-28T15:00:00Z",
                                    self.selected, self.captions, self.queue, self.now)
        self.assertTrue(path.is_file())
        self.assertEqual(record["status"], "queued_not_published")
        self.assertFalse(record["publishing_enabled"])
        self.assertEqual(json.loads(path.read_text())["caption"], "A quiet moment.")

    def test_can_explicitly_enable_metricool_scheduling(self):
        path, record = prepare_post("alicia.png", "2026-10-28T15:00:00Z",
                                    self.selected, self.captions, self.queue, self.now,
                                    publishing_enabled=True)
        self.assertEqual(record["status"], "queued_for_metricool")
        self.assertTrue(record["publishing_enabled"])
        self.assertTrue(json.loads(path.read_text())["publishing_enabled"])

    def test_boolean_parser_rejects_ambiguous_values(self):
        self.assertTrue(_parse_bool("true"))
        self.assertFalse(_parse_bool("false"))
        with self.assertRaisesRegex(ValueError, "true or false"):
            _parse_bool("maybe")

    def test_refuses_duplicate_queue_entry(self):
        prepare_post("alicia.png", "2026-10-28T15:00:00Z",
                     self.selected, self.captions, self.queue, self.now)
        with self.assertRaises(FileExistsError):
            prepare_post("alicia.png", "2026-10-29T15:00:00Z",
                         self.selected, self.captions, self.queue, self.now)

    def test_requires_matching_caption_image(self):
        record = json.loads((self.captions / "alicia.json").read_text())
        record["image"] = "other.png"
        (self.captions / "alicia.json").write_text(json.dumps(record))
        with self.assertRaisesRegex(ValueError, "different image"):
            prepare_post("alicia.png", "2026-10-28T15:00:00Z",
                         self.selected, self.captions, self.queue, self.now)

    def test_rejects_path_traversal(self):
        with self.assertRaisesRegex(ValueError, "only the image filename"):
            prepare_post("../alicia.png", "2026-10-28T15:00:00Z",
                         self.selected, self.captions, self.queue, self.now)


if __name__ == "__main__":
    unittest.main()
