import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from scripts.sync_metricool_queue import (
    build_image_url, caption_text, parse_scheduled_time, sync_queue,
)


class FakeResponse:
    def __init__(self, data, status_code=200):
        self.data, self.status_code = data, status_code

    def json(self):
        return self.data


class FakeSession:
    def __init__(self):
        self.calls = []

    def request(self, method, url, **kwargs):
        self.calls.append((method, url, kwargs))
        if url.endswith("/actions/normalize/image/url"):
            return FakeResponse({"mediaId": "media-123"})
        if url.endswith("/v2/scheduler/posts"):
            return FakeResponse({"id": "post-456"})
        return FakeResponse({}, 404)


class MetricoolQueueTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.queue, self.selected = root / "queue", root / "selected"
        self.queue.mkdir()
        self.selected.mkdir()
        self.now = datetime(2026, 10, 26, 12, 0, tzinfo=timezone.utc)
        (self.selected / "alicia.png").write_bytes(b"png")
        self.path = self.queue / "alicia.json"
        self.record = {
            "image": "alicia.png", "caption": "A quiet moment.",
            "hashtags": ["#Alicia", "#Lifestyle"],
            "scheduled_at_utc": "2026-10-28T15:00:00Z",
            "status": "queued_for_metricool", "publishing_enabled": True,
        }
        self.path.write_text(json.dumps(self.record), encoding="utf-8")
        self.env = {"METRICOOL_API_TOKEN": "token", "METRICOOL_USER_ID": "123", "METRICOOL_BLOG_ID": "456"}

    def tearDown(self):
        self.temp.cleanup()

    def test_image_url_is_public_and_stable(self):
        self.assertEqual(
            build_image_url("alicia.png"),
            "https://raw.githubusercontent.com/arturwarlord/instagram-ai-agent/main/content/selected/alicia.png",
        )

    def test_rejects_timestamp_without_timezone(self):
        with self.assertRaisesRegex(ValueError, "include a timezone"):
            parse_scheduled_time("2026-10-28T15:00:00", self.now)

    def test_caption_includes_hashtags(self):
        self.assertEqual(caption_text(self.record), "A quiet moment.\n\n#Alicia #Lifestyle")

    def test_dry_run_never_calls_api_or_changes_queue(self):
        session = FakeSession()
        out = sync_queue(self.queue, self.selected, env={}, dry_run=True, now=self.now, session=session)
        self.assertEqual(out["dry_run"], 1)
        self.assertEqual(session.calls, [])
        self.assertEqual(json.loads(self.path.read_text())["status"], "queued_for_metricool")

    def test_disabled_entry_is_skipped_without_api_secrets(self):
        rec = dict(self.record, publishing_enabled=False, status="queued_not_published")
        self.path.write_text(json.dumps(rec), encoding="utf-8")
        out = sync_queue(self.queue, self.selected, env={}, now=self.now, session=FakeSession())
        self.assertEqual(out["skipped"], 1)
        self.assertEqual(out["submitted"], 0)

    def test_enabled_entry_requires_api_secrets(self):
        with self.assertRaisesRegex(RuntimeError, "METRICOOL_API_TOKEN"):
            sync_queue(self.queue, self.selected, env={}, now=self.now, session=FakeSession())

    def test_success_normalizes_media_and_schedules_post(self):
        session = FakeSession()
        out = sync_queue(self.queue, self.selected, env=self.env, now=self.now, session=session)
        self.assertEqual(out["submitted"], 1)
        self.assertEqual(len(session.calls), 2)
        _, _, call = session.calls[1]
        self.assertEqual(call["params"], {"userId": "123", "blogId": "456"})
        self.assertEqual(call["json"]["providers"], [{"network": "instagram"}])
        self.assertEqual(call["json"]["media"], {"mediaId": "media-123"})
        self.assertTrue(call["json"]["autoPublish"])
        saved = json.loads(self.path.read_text())
        self.assertEqual(saved["status"], "submitted_to_metricool")
        self.assertEqual(saved["metricool_post_id"], "post-456")

    def test_api_error_does_not_mark_queue_submitted(self):
        class FailedSession:
            def request(self, method, url, **kwargs):
                return FakeResponse({}, status_code=401)
        out = sync_queue(self.queue, self.selected, env=self.env, now=self.now, session=FailedSession())
        self.assertEqual(len(out["errors"]), 1)
        self.assertEqual(json.loads(self.path.read_text())["status"], "queued_for_metricool")


if __name__ == "__main__":
    unittest.main()
