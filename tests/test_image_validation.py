import io
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from ai.image_generator import _is_duplicate_image, _validate_image_bytes


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

    def test_allows_different_image(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            (folder / "previous.png").write_bytes(make_png(color=(30, 120, 200)))
            self.assertFalse(_is_duplicate_image(make_png(color=(200, 20, 30)), folder))


if __name__ == "__main__":
    unittest.main()
