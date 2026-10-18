import io
import json
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from PIL import Image, ImageDraw

from ai.image_generator import (
    _choose_visual_variation,
    _is_duplicate_image,
    _validate_image_bytes,
)


def make_png(width=640, height=800, color=(30, 120, 200)):
    buffer = io.BytesIO()
    Image.new("RGB", (width, height), color).save(buffer, format="PNG")
    return buffer.getvalue()


class GeneratedImageValidationTests(unittest.TestCase):
    def test_accepts_valid_image_and_returns_dimensions(self):
        self.assertEqual(_validate_image_bytes(make_png()), (640, 800))

    def test_rejects_empty_bytes(self):
        with self.assertRaisesRegex(RuntimeError, "empty image"):
            _validate_image_bytes(b"")

    def test_rejects_corrupt_image(self):
        with self.assertRaisesRegex(RuntimeError, "not a valid image"):
            _validate_image_bytes(b"not an image")

    def test_rejects_image_below_minimum_dimensions(self):
        with self.assertRaisesRegex(RuntimeError, "too small"):
            _validate_image_bytes(make_png(320, 400))

    def test_detects_same_pixels_in_existing_png(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            (folder / "previous.png").write_bytes(make_png())
            self.assertTrue(_is_duplicate_image(make_png(), folder))


    def test_detects_near_identical_image_with_small_visual_change(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            original = Image.new("RGB", (640, 800), (120, 150, 180))
            draw = ImageDraw.Draw(original)
            draw.rectangle((100, 100, 500, 700), fill=(170, 190, 210))
            original.save(folder / "previous.png", format="PNG")

            slightly_changed = original.copy()
            ImageDraw.Draw(slightly_changed).rectangle(
                (101, 100, 500, 700), fill=(170, 190, 210)
            )
            buffer = io.BytesIO()
            slightly_changed.save(buffer, format="PNG")

            self.assertTrue(_is_duplicate_image(buffer.getvalue(), folder))

    def test_allows_visually_different_images(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            Image.new("RGB", (640, 800), (20, 30, 220)).save(
                folder / "previous.png", format="PNG"
            )
            self.assertFalse(_is_duplicate_image(make_png(color=(220, 30, 20)), folder))

    def test_avoids_recent_visual_combination_and_individual_choices(self):
        with tempfile.TemporaryDirectory() as directory:
            history_file = Path(directory) / "history.json"
            previous = {
                "composition": "composition A",
                "pose": "pose A",
                "gaze": "gaze A",
            }
            history_file.write_text(json.dumps([previous]), encoding="utf-8")

            with patch("ai.image_generator.HISTORY_FILE", history_file):
                selected = _choose_visual_variation(
                    ["composition A", "composition B"],
                    ["pose A", "pose B"],
                    ["gaze A", "gaze B"],
                )

            self.assertEqual(
                selected,
                ("composition B", "pose B", "gaze B"),
            )

    def test_allows_different_image(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            (folder / "previous.png").write_bytes(make_png(color=(30, 120, 200)))
            self.assertFalse(_is_duplicate_image(make_png(color=(200, 20, 30)), folder))


if __name__ == "__main__":
    unittest.main()
