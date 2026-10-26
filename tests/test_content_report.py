import tempfile
import unittest
from pathlib import Path

from scripts.content_report import build_report


class ContentReportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.generated = root / "generated"
        self.selected = root / "selected"
        self.captions = root / "captions"
        self.queue = root / "queue"
        for directory in (self.generated, self.selected, self.captions, self.queue):
            directory.mkdir()
        (self.generated / "generated.png").write_bytes(b"png")
        (self.selected / "alicia.png").write_bytes(b"png")
        (self.captions / "alicia.json").write_text(
            '{"image":"alicia.png","status":"draft_not_published","caption":"Hello"}',
            encoding="utf-8",
        )
        (self.queue / "alicia.json").write_text(
            '{"image":"alicia.png","status":"queued_not_published",'
            '"scheduled_at_utc":"2026-10-28T15:00:00Z","publishing_enabled":false}',
            encoding="utf-8",
        )

    def tearDown(self):
        self.temp.cleanup()

    def report(self):
        return build_report(self.generated, self.selected, self.captions, self.queue)

    def test_report_lists_assets_and_queue_status(self):
        report = self.report()
        self.assertIn("generated.png", report)
        self.assertIn("alicia.png", report)
        self.assertIn("draft_not_published", report)
        self.assertIn("queued_not_published", report)
        self.assertIn("2026-10-28T15:00:00Z", report)

    def test_missing_caption_and_queue_are_reported(self):
        (self.captions / "alicia.json").unlink()
        (self.queue / "alicia.json").unlink()
        report = self.report()
        self.assertIn("| `alicia.png` | no | yes | missing | missing | — |", report)

    def test_invalid_json_is_reported_without_crashing(self):
        (self.captions / "broken.json").write_text("{not json", encoding="utf-8")
        report = self.report()
        self.assertIn("Data warnings", report)
        self.assertIn("broken.json", report)

    def test_empty_content_has_clear_message(self):
        for directory in (self.generated, self.selected, self.captions, self.queue):
            for path in directory.iterdir():
                path.unlink()
        self.assertIn("No content files found yet", self.report())

    def test_report_describes_read_only_boundary(self):
        report = self.report()
        self.assertIn("never performs Metricool or Instagram API operations", report)
        self.assertIn("publishing_enabled: true", report)


if __name__ == "__main__":
    unittest.main()
